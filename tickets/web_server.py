#!/usr/bin/python
# -*- coding: utf-8 -*-

# Flask libraries
from flask import Flask, render_template, request, redirect, Markup
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Standard python libraries
import httplib2, json, requests, random, string

from tickets import DBSession, Conference, Team, Game, Ticket, Ticket_Lot, User

app = Flask(__name__)
db_session = DBSession()

DEBUG = True
LOG_ERRORS = True

#------------------------------------------------------------------------------------
# some helper functions

# gen_response() is just a little wrapper around make_response()
# to make the code below more readable.
#
def gen_response(msg, rc=401, content_type='application/json'):
    if DEBUG or LOG_ERRORS:
        print msg
    response = make_response(json.dumps(msg), rc)
    response.headers['Content-Type'] = content_type
    return response

# so we can see what we're working with
def show_login_session():
    for key in login_session.keys():
        print "%s: %s" % (key, login_session[key])

# add a user to the database
#
def createUser(login_session):
    user = User(
        name = login_session['username'],
        email = login_session['email'],
        picture = login_session['picture']
    )
    db_session.add(user)
    db_session.commit()
    return user.id

# maps a user_id to a user
#
def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user

# lookup a user by their email address
# and return the user id
#
def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

#------------------------------------------------------------------------------------
# Google+ Authorization

google_client_secrets_file = 'oauth/google/google_client_secrets.json'
f = open(google_client_secrets_file, 'r')
google_client_secrets = json.load(f)
f.close()

@app.route('/gconnect', methods=['POST'])
def gconnect():

    if request.args.get('state') != login_session['state']:
        msg = 'Invalid state parameter'
        return gen_response(msg)

    # state token matches so we use the one time auth_code
    auth_code = request.data
    try:
        # upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(google_client_secrets_file, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(auth_code)

    except FlowExchangeError:
        msg = 'Failed to upgrade the authorization code.'
        return gen_response(msg)

    # Check that the access token is valid.
    token = credentials.access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
    result = json.loads(httplib2.Http().request(url % token, 'GET')[1])
            
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        msg = result.get('error')
        return gen_response(msg, rc=500)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        msg = "Token's user ID doesn't match given user ID."
        return gen_response(msg)

    if result['issued_to'] != google_client_secrets['web']['client_id']:
        msg = "Token's client ID does not match app_id."
        return gen_response(msg)

    # Check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if (stored_credentials is not None) and (gplus_id == stored_gplus_id):
        msg = 'Current user is already connected.'
        return gen_response(msg, rc=200)

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("you are now logged in as %s" % login_session['username'])
    return redirect('/conferences')

# Logout - Revoke a current user's token and reset their login session
#

def gdisconnect():

    credentials = login_session.get('credentials')
    if credentials is None:
        msg = 'Current user not connected.'
        return gen_response(msg)
    access_token = credentials.access_token

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    result = httplib2.Http().request(url, 'GET')[0]

#------------------------------------------------------------------------------------
# Facebook Authorization

fb_client_secrets_file = 'oauth/fb/fb_client_secrets.json'
f = open(fb_client_secrets_file, 'r')
fb_client_secrets = json.load(f)
f.close()
    
@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    print "access token received %s " % access_token

    app_id = fb_client_secrets['web']['app_id']
    app_secret = fb_client_secrets['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?'
    url += 'grant_type=fb_exchange_token'
    url += '&client_id=%s' % app_id
    url += '&client_secret=%s' % app_secret
    url += '&fb_exchange_token=%s' % access_token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?'
    url += '%s&' % token
    url += 'fields=name,id,email'

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to 
    # properly logout, let's strip out the information before 
    # the equals sign in our token
    
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token
    
    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?'
    url += '%s&' % token
    url += 'redirect=0&'
    url += 'height=200&'
    url += 'width=200'

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, %s!</h1>' % login_session['username']
    output += '<img src="%s"' % login_session['picture']
    output += ' style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

def fbdisconnect():

    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/' % facebook_id
    url += 'permissions?access_token=%s' % access_token

    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]


#-------------------------------------------------------------------------
# Tickets 'R' Us App 

# login
#        
@app.route('/login')
def login():

    #show_login_session()
    state = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state

    fb_app_id = '907786629329598'
    fb_connect_js = Markup(render_template(
        'fb_connect.js',
        fb_app_id = fb_app_id,
        STATE = state,
        redirect_url = url_for("conferences")
    ))

    google_app_id = "123296537254-thk0g1ciqscu3itopc5e8q8q6nps6iob.apps.googleusercontent.com"    
    google_connect_js = Markup(render_template(
        'google_connect.js',
        STATE = state,
        redirect_url = url_for("conferences")
    ))

    return render_template(
        'login.html', 
        google_app_id = google_app_id,
        google_connect_js = google_connect_js,
        fb_connect_js = fb_connect_js,
        google_sign_in = True,
        login_session = login_session
    )

# logout
#
@app.route('/disconnect')
def disconnect():

    if 'provider' in login_session.keys():

        if login_session['provider'] == 'google':
            gdisconnect()

        if login_session['provider'] == 'facebook':
            fbdisconnect()

        # If login_session gets in to a bad state
        # it seems to want to persist, so let's just
        # clean it up.
        for key in login_session.keys():
            del login_session[key]

        flash("You have successfully been logged out.")
        return redirect(url_for('conferences'))


# the main page shows all the conferences
#
@app.route('/')
@app.route('/conferences')
def conferences():
    #show_login_session()
    conferences = db_session.query(Conference).all()
    main = Markup(render_template('conferences.html', conferences=conferences))
    return render_template('layout.html', main=main, login_session=login_session)


# a page for a single conference
# it shows the schedules for each team
#
@app.route('/conference/<conference>')
def conference(conference):
    conference = db_session.query(Conference).filter_by(abbrev_name=conference).one()
    main = Markup(render_template('conference.html', conference=conference))
    return render_template('layout.html', main=main, login_session=login_session)

@app.route('/conference/<conference>/JSON')
def conference_json(conference):
    conference = db_session.query(Conference).filter_by(abbrev_name=conference).one()
    return jsonify(conference.serialize())

# TODO: I don't think this is used anymore.
# Delete it ?
#
@app.route('/team/<team_name>')
def team(team_name):
    team = db_session.query(Team).filter_by(name=team_name).one()
    return render_template('team.html', team=team)

@app.route('/team/<team_name>/JSON')
def team_json(team_name):
    team = db_session.query(Team).filter_by(name=team_name).one()
    return jsonify(team.serialize())

# The game page shows the tickets available for purchase
# for that game.
#
@app.route('/game/<game_id>')
def game(game_id):
    game = db_session.query(Game).filter_by(id=game_id).one()
    game.ticket_lots.sort(key = lambda x: x.price)
    main = Markup(render_template('game_tickets.html', game=game))
    return render_template('layout.html', main=main, login_session=login_session)

#---------------------------------------------------------------------------------------------
# Sell Tickets

# The GET method retrieves the interface and 
# the POST method does the work
# 
@app.route('/game/<game_id>/sell', methods=['GET', 'POST'])
def sell_tickets(game_id):

    if 'user_id' not in login_session:
        print "You must be logged in to sell tickets!"
        flash("You must be logged in to sell tickets!")
        return redirect(url_for('game', game_id=game_id))

    # user is logged in so able to sell tickets
    # return a page with a fill-in form
    if request.method == 'GET':
        game = db_session.query(Game).filter_by(id=game_id).one()
        main = Markup(render_template('sell_tickets.html', game=game, login_session=login_session))
        return render_template('layout.html', main=main, login_session=login_session)

    # process a submitted form for selling tickets
    elif request.method == 'POST':

        # get the information we need from the form
        try:
            seller_id = request.form['user_id']
            game_id = request.form['game_id']
            section =  request.form['section']
            row = request.form['row']
            price = request.form['price']
            seat = int(request.form['first_seat'])
            num_seats = int(request.form['num_seats'])

        except:
            print "sell_tickets(): bad form data"
            flash("sell_tickets(): bad form data")
            return redirect(url_for('game', game_id=game_id))

        # ok, got the info
        # add the tickets to the database
        try:
            ticket_lot = Ticket_Lot
                seller_id = seller_id,
                game_id = game_id,
                section =  section,
                row = row,
                price = price
            )
            db_session.add( ticket_lot)

            for j in range(num_seats):
                db_session.add( Ticket(
                    lot = ticket_lot,
                    seat = seat + j
                ))
            db_session.commit()

        except:
            print "sell_tickets(): could not commit transaction"
            flash("sell_tickets(): could not commit transaction")
            return redirect(url_for('game', game_id=game_id))
            
        # redirect to the game page where
        # the newly added tickets should be visible
        return redirect(url_for('game', game_id=game_id))

@app.route('/game/<game_id>/JSON')
def game_json(game_id):
    game = db_session.query(Game).filter_by(id=game_id).one()
    return jsonify(game.serialize())


# ticket_lot() returns a page showing the group of tickets
# that are being offered for sale together.
#
@app.route('/tickets/<ticket_lot_id>')
def ticket_lot(ticket_lot_id):
    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    main = Markup(render_template('ticket_lot.html', ticket_lot=ticket_lot, login_session=login_session))
    return render_template('layout.html', main=main, login_session=login_session)

@app.route('/tickets/<ticket_lot_id>/JSON')
def ticket_lot_json(ticket_lot_id):
    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    return jsonify(ticket_lot.serialize())

#---------------------------------------------------------------------------------------------
# Edit Tickets

# I decided that the only thing it made sense to edit was the price.
# If any of the other stuff is wrong, the ticket_lot can be deleted
# and replaced.

@app.route('/tickets/<ticket_lot_id>/edit', methods=['GET', 'POST'])
def edit_tickets(ticket_lot_id):

    if 'user_id' not in login_session:
        print "You must be logged in to edit tickets!"
        flash("You must be logged in to edit tickets!")
        return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))

    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    if ticket_lot.seller_id != login_session['user_id']:
        print "You cannot edit another user's tickets!"
        flash("You cannot edit another user's tickets!")
        return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))

    if request.method == 'GET':
        ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
        main = Markup(render_template(
            'edit_tickets.html', ticket_lot=ticket_lot, login_session=login_session))
        return render_template('layout.html', main=main, login_session=login_session)

    elif request.method == 'POST':
        try:
            ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
            ticket_lot.price = request.form['price']
            db_session.commit()
        except:
            print "edit_tickets(): could not commit transaction"
            flash("edit_tickets(): could not commit transaction")
            return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))
            
        return redirect(url_for('game', game_id=ticket_lot.game_id))

#---------------------------------------------------------------------------------------------
# Delete Tickets

@app.route('/tickets/<ticket_lot_id>/delete', methods=['GET', 'POST'])
def delete_tickets(ticket_lot_id):

    if 'user_id' not in login_session:
        print "You must be logged in to delete tickets!"
        flash("You must be logged in to delete tickets!")
        return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))

    ticket_lot = db_session.query(Ticket_Lot).filter_by(id=ticket_lot_id).one()
    if ticket_lot.seller_id != login_session['user_id']:
        print "You cannot delete another user's tickets!"
        flash("You cannot delete another user's tickets!")
        return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))

    if request.method == 'GET':
        main = Markup(render_template(
            'delete_tickets.html', ticket_lot=ticket_lot, login_session=login_session))
        return render_template('layout.html', main=main, login_session=login_session)

    elif request.method == 'POST':
        try:
            game_id = ticket_lot.game_id
            for ticket in ticket_lot.tickets:
                db_session.delete(ticket)
            db_session.delete(ticket_lot)
            db_session.commit()
        except:
            print "delete_tickets(): could not commit transaction"
            flash("delete_tickets(): could not commit transaction")
            return redirect(url_for('tickets', ticket_lot_id=ticket_lot_id))

        flash("Tickets successfully deleted.")
        return redirect(url_for('game', game_id=game_id))
 
       
# TODO: I don't think this does anything yet !-)
#
@app.route('/users')
def users():
    users = db_session.query(User).all()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    main = Markup(render_template('user.html', user=user))
    return render_template('layout.html', main=main, login_session=login_session)

@app.route('/users/<int:user_id>/JSON')
def user_json(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return jsonify(user.serialize())



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
