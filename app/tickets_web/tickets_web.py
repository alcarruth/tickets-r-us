#!/usr/bin/python
# -*- coding: utf-8 -*-

# Flask libraries
from flask import Flask, render_template, request, redirect, Markup
from flask import jsonify, url_for, flash, make_response
from flask import session as app_session
from flask_seasurf import SeaSurf

# Standard python libraries
import httplib2, json, requests, random, string, os, sys
from functools import wraps
from dict2xml import dict2xml as xmlify

# I need something like these to handle the file upload.
# If I understand it correctly (doubtful !-) the examples found at
# http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# seem to trust the filename extension.  It seems to me that we
# should verify the file type somehow and give it the appropriate
# extension, .jpg, .png etc.

import imghdr
from werkzeug import secure_filename

# The tickets database definitions are in tickets.py
from tickets_db import DBSession, Conference, Team, Game, Ticket, Ticket_Lot, User, startup_info
from tickets_db import createUser, getUserByEmail, getUserByID

app = Flask(__name__)

# Prevent cross-site request forgery
# Hidden '_csrf_token' fields have been added to the forms in the
# templates sell_tickets.html, edit_tickets.html and delete_tickets.html.
# See https://flask-seasurf.readthedocs.org/en/latest/
csrf = SeaSurf(app)

db_session = DBSession()

# The OAuth2 stuff has been moved to separate files:
#  - google_auth.py    and
#  - facebook_auth.py.

# The auth code needs access to the db_session
# so we set that above and then use the separate code to produce
# the connect and disconnect functions, below.  The routes are set in the 
# respective (google or fb) auth functions.

from auth.google import Google_Auth_Client
from auth.facebook import Facebook_Auth_Client

import settings

# These are used in functions connect() and disconnect() below and in the
# template login.html.

# TODO: move specific html for the auth buttons to the respective python 
# files and change login.html to iterate over auth_providers to create the 
# buttons for the authentication providers included below.
auth_providers = {
    'google': Google_Auth_Client(settings.google_secrets_file),
    'facebook': Facebook_Auth_Client(settings.facebook_secrets_file)
}

DEBUG = True
LOG_ERRORS = True

#------------------------------------------------------------------------------------
# Helper function gen_response() is just a little wrapper around
# make_response() to make the code below more readable.
#
# TODO: this could do more, like have an error notification  page with 
# a 'Continue' button which would either take you to the main page
# or perhaps to where you were before the error.  Give it some thought.
#
def gen_response(msg, rc=401, content_type='application/json'):
    if DEBUG or LOG_ERRORS:
        print msg
    response = make_response(json.dumps(msg), rc)
    response.headers['Content-Type'] = content_type
    return response


#------------------------------------------------------------------------------------
# Authentication and Authorization View Decorators
# 
# We have here two view decorators: check_authentication() and
# auth_required() Each of them takes an arg 'msg' which is to be
# flashed.  For example usage see sell_tickets(), edit_tickets() and
# delete_tickets() below.


# Function check_authentication() returns a decorator for wrapping
# those functions which require that the user be logged in.  If used,
# check_authentication() should be placed inside the app.route()
# decorator.
#
def check_authentication(msg):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in app_session:
                flash(msg)
                # The keyword arg 'next_url' is used in function login() 
                # in the call to redirect().  So we attempt the login and
                # then return to the page that required the login.
                return redirect(url_for('login', next_url=request.url))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Function check_authorization() returns a decorator for wrapping
# those functions that require authorized access. If used,
# check_authorization() should be placed inside the
# check_authentication() decorator.
#
def check_authorization(msg, item_class, end_point):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            item_id = kwargs['item_id']
            item = db_session.query(item_class).filter_by(id=item_id).one()
            if item.user_id != app_session['user_id']:
                flash(msg)
                return redirect(url_for(end_point, item_id=item_id))
            # We have already looked up the item so why have function f()
            # do it again?  So we have the following statement and we change
            # the endpoints that use this decorator to have the 'item' arg.
            # (I guess this makes the item_id arg superfluous.)
            kwargs['item'] = item
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_session_id():
    if not app_session.has_key('session_id'):
        app_session['session_id'] = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
    return app_session.get('session_id')

#----------------------------------------------------------------------------------
# Tickets 'R' Us App 

mount_point = '/tickets'

# login

class Login:

    def __init__(self, provider_name, access_token, access_id, user_data):
        self.provider_name = provider_name
        self.access_token = access_token
        self.access_id = access_id
        self.user_data = user_data

    def to_json(self):
        return json.dumps( {
            'provider_name': self.provider_name,
            'access_token': self.access_token,
            'access_id': self.access_id,
            'user_data': self.user_data } )

    def from_json(self, login_json):
        d = json.loads(login_json)
        self.provider_name = d['provider_name']
        self.access_token = d['access_token']
        self.access_id = d['access_id']
        self.user_data = d['user_data']

@app.route(mount_point + '/login')
def login():

    # TODO: next_url wasn't working with https
    redirect_path = request.args.get('next_url') or url_for('conferences')
    redirect_url = 'https://armazilla.net' + redirect_path
    print >>sys.stdout, redirect_url
    session_id = get_session_id()

    # Facebook login
    fb_app_id = '907786629329598'
    fb_connect_js = Markup(render_template(
        'fb_connect.js',
        fb_app_id = fb_app_id,
        SESSION_ID = session_id,
        redirect_url = redirect_url
    ))

    # Google login
    google_app_id = auth_providers['google'].client_id
    google_connect_js = Markup(render_template(
        'google_connect.js',
        SESSION_ID = session_id,
        redirect_url = redirect_url
    ))

    return render_template(
        'login.html', 
        google_app_id = google_app_id,
        google_connect_js = google_connect_js,
        fb_connect_js = fb_connect_js,
        google_sign_in = True,
        app_session = app_session
    )


@csrf.exempt
@app.route(mount_point + '/connect/<provider_name>/<session_id>', methods=['POST'])
def connect(provider_name, session_id):

    print "\n\nprovider_name: %s\n" % provider_name
    print "session_id: %s\n" % session_id

    # TODO: Fix this hack:
    redirect_url = 'https://armazilla.net/tickets/conferences'

    # verify session_id
    print "get_session_id(): %s\n" % get_session_id()
    if session_id != get_session_id():
        flash('Invalid session_id.')
        return redirect(redirect_url)

    # auth_code is in the 'POST' data
    auth_code = request.data
    print "auth_code: %s\n" % auth_code
    login = auth_providers[provider_name].connect(auth_code, Login)

    if (app_session.get('login') is not None):
        prev_login = Login(None, None, None, None)
        prev_login.from_json(app_session.get('login'))
        if login.get('access_id') == prev_login.get('access_id'):
            msg = 'Current user is already connected.'
            flash(msg)
            return redirect(redirect_url)
            
    user = getUserByEmail(db_session, login.user_data['email'])
    if not user:
        user = createUser(db_session, login.user_data)

    # Store the access token in the session for later use.
    app_session['login'] = login.to_json()
    app_session['user_id'] = user.id
    app_session['user_name'] = user.name

    msg = "you are now logged in as %s" % user.name
    flash(msg)
    return redirect(redirect_url)


# logout
#
@csrf.exempt
@app.route(mount_point + '/disconnect')
def disconnect():

    # TODO: Fix this hack:
    redirect_url = 'https://armazilla.net/tickets/conferences'

    try:
        login_json = app_session.get('login')
        login = json.loads(login_json)
        provider = auth_providers[login.get('provider_name')]
        result = provider.disconnect(login)
        del app_session['login']
        del app_session['user_id']
        del app_session['user_name']
        msg = "You have successfully logged out."
        flash(msg)

    except:
        msg = "You are not logged in."
        flash(msg)

    return redirect(redirect_url)


#---------------------------------------------------------------------------------------------
# Landing View

@app.route(mount_point + '/')
def landing():
    main = Markup(render_template('landing.html'))
    return render_template('layout.html', main=main, app_session=app_session)



#---------------------------------------------------------------------------------------------
# Conferences View

@app.route(mount_point + '/conferences')
def conferences():
    conferences = db_session.query(Conference).all()
    main = Markup(render_template('conferences.html', conferences=conferences))
    return render_template('layout.html', main=main, app_session=app_session)



#---------------------------------------------------------------------------------------------
# Conference Views

# a page for a single conference
# it shows the schedules for each team
#
@app.route(mount_point + '/conference/<conference>')
def conference(conference):
    conference = db_session.query(Conference).filter_by(abbrev_name=conference).one()
    main = Markup(render_template('conference.html', conference=conference))
    return render_template('layout.html', main=main, app_session=app_session)

@app.route(mount_point + '/conference/<conference>/JSON')
def conference_json(conference):
    conference = db_session.query(Conference).filter_by(abbrev_name=conference).one()
    return jsonify(conference.to_dict())

@app.route(mount_point + '/conference/<conference>/XML')
def conference_xml(conference):
    conference = db_session.query(Conference).filter_by(abbrev_name=conference).one()
    return xmlify(conference.to_dict())



#---------------------------------------------------------------------------------------------
# Team Views

# TODO: I don't think this is used anymore.  Delete it ?  No, don't
# delete it.  It could be used later on to provide more information
# about a team / school on a new page.

@app.route(mount_point + '/team/<team_name>')
def team(team_name):
    team = db_session.query(Team).filter_by(name=team_name).one()
    return render_template('team.html', team=team)

@app.route(mount_point + '/team/<team_name>/JSON')
def team_json(team_name):
    team = db_session.query(Team).filter_by(name=team_name).one()
    return jsonify(team.to_dict())

@app.route(mount_point + '/team/<team_name>/XML')
def team_xml(team_name):
    team = db_session.query(Team).filter_by(name=team_name).one()
    return xmlify(team.to_dict())



#---------------------------------------------------------------------------------------------
# Game Views

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])

# The game page shows the tickets available for purchase
# for that game.
#
@app.route(mount_point + '/game/<int:game_id>')
def game(game_id):
    game = db_session.query(Game).filter_by(id=game_id).one()
    game.ticket_lots.sort(key = lambda x: x.price)
    main = Markup(render_template('game_tickets.html', game=game))
    return render_template('layout.html', main=main, app_session=app_session)


# Sell Tickets

@app.route(mount_point + '/game/<int:game_id>/sell', methods=['GET', 'POST'])
@check_authentication("You must be logged in to sell tickets!")
def sell_tickets(game_id):

    # user is logged in so able to sell tickets
    # return a page with a fill-in form
    if request.method == 'GET':
        game = db_session.query(Game).filter_by(id=game_id).one()
        main = Markup(render_template('sell_tickets.html', game=game, app_session=app_session))
        return render_template('layout.html', main=main, app_session=app_session)

    # process a submitted form for selling tickets
    elif request.method == 'POST':

        # get the information we need from the form
        try:
            user_id = request.form['user_id']
            game_id = request.form['game_id']
            section =  request.form['section']
            row = request.form['row']
            price = request.form['price']
            seat = int(request.form['first_seat'])
            num_seats = int(request.form['num_seats'])
            img = request.files['img']

        except:
            msg = "sell_tickets(): bad form data"
            flash(msg)
            return redirect(url_for('game', game_id=game_id))

        # ok, got the info
        # add the tickets to the database
        try:
            ticket_lot = Ticket_Lot(
                user_id = user_id,
                game_id = game_id,
                section =  section,
                row = row,
                price = price,
                img_path = None
            )
            db_session.add( ticket_lot)
            db_session.commit()
            if img:
                img_type = imghdr.what(img)
                if img_type in ['jpeg', 'png']:
                    # Unlike in all the examples on the Flask website,
                    # the path must be relative to the website root in order
                    # for img.save() to work.  This makes sense to me, but 
                    # why do the examples have a leading '/' ?
                    # http://flask.pocoo.org/docs/0.10/quickstart/#file-uploads
                    # http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
                    img_dir = mount_point + '/static/images/tickets/'
                    img_file = 'ticket_lot_%d.%s' % (ticket_lot.id, img_type)
                    ticket_lot.img_path = img_dir + img_file
                    img.save(ticket_lot.img_path)

            for j in range(num_seats):
                db_session.add( Ticket(
                    lot = ticket_lot,
                    seat = seat + j
                ))
            db_session.commit()

        except:
            flash("sell_tickets(): could not commit transaction")
            return redirect(url_for('game', game_id=game_id))
            
        # redirect to the game page where
        # the newly added tickets should be visible
        return redirect(url_for('game', game_id=game_id))

@app.route(mount_point + '/game/<int:game_id>/JSON')
def game_json(game_id):
    game = db_session.query(Game).filter_by(id=game_id).one()
    return jsonify(game.to_dict())

@app.route(mount_point + '/game/<int:game_id>/XML')
def game_xml(game_id):
    game = db_session.query(Game).filter_by(id=game_id).one()
    return xmlify(game.to_dict())



#---------------------------------------------------------------------------------------------
# Tickets Views



# ticket_lot() returns a page showing the group of tickets
# that are being offered for sale together.
#
@app.route(mount_point + '/ticket_lot/<int:item_id>')
def ticket_lot(item_id):
    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=item_id).one()

    # TODO: 
    # edit tiket_lot.html to display tickets image

    main = Markup(render_template('ticket_lot.html', ticket_lot=ticket_lot, app_session=app_session))
    return render_template('layout.html', main=main, app_session=app_session)

@app.route(mount_point + '/ticket_lot/<int:item_id>/JSON')
def ticket_lot_json(item_id):
    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=item_id).one()
    return jsonify(ticket_lot.to_dict())

@app.route(mount_point + '/ticket_lot/<int:item_id>/XML')
def ticket_lot_xml(item_id):
    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=item_id).one()
    return xmlify(ticket_lot.to_dict())



# Edit Tickets

# I decided that the only thing it made sense to edit was the price.
# If any of the other stuff is wrong, the ticket_lot can be deleted
# and replaced.

@app.route(mount_point + '/ticket_lot/<int:item_id>/edit', methods=['GET', 'POST'])
@check_authentication("You must be logged in to edit tickets!")
@check_authorization("You cannot edit another user's tickets!", Ticket_Lot, 'ticket_lot')
def edit_tickets(item_id, item):

    ticket_lot = item
    #ticket_lot = db_session.query(Ticket_Lot).filter_by(id=item_id).one()

    if request.method == 'GET':
        main = Markup(render_template(
            'edit_tickets.html', ticket_lot=ticket_lot, app_session=app_session))
        return render_template('layout.html', main=main, app_session=app_session)

    elif request.method == 'POST':

    # TODO: 
    # Handle uploaded ticket image.
    # Add image to the static dir.
    # Add image url to db entry.

        try:
            ticket_lot.price = request.form['price']
            if request.files.has_key('img'):
                img = request.files['img']
                img_type = imghdr.what(img)
                if img_type in ['jpeg', 'png']:
                    # Unlike in all the examples on the Flask website,
                    # the path must be relative to the website root in order
                    # for img.save() to work.  This makes sense to me, but 
                    # why do the examples have a leading '/' ?
                    # http://flask.pocoo.org/docs/0.10/quickstart/#file-uploads
                    # http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
                    img_dir = mount_point + '/static/images/tickets/'
                    img_file = 'ticket_lot_%d.%s' % (ticket_lot.id, img_type)
                    ticket_lot.img_path = img_dir + img_file
                    img.save(ticket_lot.img_path)

            db_session.commit()
        except:
            msg = "edit_tickets(): could not commit transaction"
            flash(msg)
            return redirect(url_for('ticket_lot', item_id=item_id))
            
        return redirect(url_for('game', game_id=ticket_lot.game_id))



# Delete Tickets

@app.route(mount_point + '/ticket_lot/<int:item_id>/delete', methods=['GET', 'POST'])
@check_authentication("You must be logged in to delete tickets!")
@check_authorization("You cannot delete another user's tickets!", Ticket_Lot, 'ticket_lot')
def delete_tickets(item_id, item):

    ticket_lot = item

    if request.method == 'GET':
        main = Markup(render_template(
            'delete_tickets.html', ticket_lot=ticket_lot, app_session=app_session))
        return render_template('layout.html', main=main, app_session=app_session)

    elif request.method == 'POST':

        img_path = ticket_lot.img_path
        print img_path
        if img_path:
            os.remove(img_path)
        game_id = ticket_lot.game_id
        print "game_id: %d" % game_id
        for ticket in ticket_lot.tickets:
            db_session.delete(ticket)
            db_session.delete(ticket_lot)
        try:
            db_session.commit()
        except:
            print "delete_tickets(): could not commit transaction"
            flash("delete_tickets(): could not commit transaction")
            return redirect(url_for('ticket_lot', item_id=item_id))

        flash("Tickets successfully deleted.")
        return redirect(url_for('game', game_id=game_id))


# Delete Image

@app.route(mount_point + '/ticket_lot/<int:item_id>/delete_image', methods=['GET', 'POST'])
@check_authentication("You must be logged in to delete ticket image!")
@check_authorization("You cannot delete another user's ticket image!", Ticket_Lot, 'ticket_lot')
def delete_image(item_id, item):

    ticket_lot = item

    if request.method == 'GET':
        main = Markup(render_template(
            'delete_image.html', ticket_lot=ticket_lot, app_session=app_session))
        return render_template('layout.html', main=main, app_session=app_session)

    elif request.method == 'POST':

        try:
            os.remove(ticket_lot.img_path)
            ticket_lot.img_path = None
            db_session.commit()
        except:
            print "delete_image(): could not commit transaction"
            flash("delete_image(): could not commit transaction")
            return redirect(url_for('ticket_lot', item_id=item_id))

        flash("Ticket image successfully deleted.")
        return redirect(url_for('ticket_lot', item_id=item_id))



 
#---------------------------------------------------------------------------------------------
# User Views


@app.route(mount_point + '/users')
def users():
    users = db_session.query(User).all()
    return render_template('users.html', users=users)

@app.route(mount_point + '/users/<int:user_id>')
def user(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    main = Markup(render_template('user.html', user=user))
    return render_template('layout.html', main=main, app_session=app_session)

@app.route(mount_point + '/users/<int:user_id>/JSON')
def user_json(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return jsonify(user.to_dict())

@app.route(mount_point + '/users/<int:user_id>/XML')
def user_xml(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return xmlify(user.to_dict())


# generate a random secret key
app.secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in xrange(32))

app.debug = False
print >> sys.stderr, 'tickets app loaded.'
print >> sys.stderr, app

#---------------------------------------------------------------------------------------------
# Start the server

if __name__ == '__main__':
    print startup_info

    app.run(host='0.0.0.0', port=5000)
