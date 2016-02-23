#!/usr/bin/python
# -*- coding: utf-8 -*-

from auth_common import *

# google_auth()
#
def google_auth(app, secrets_file):

    f = open(secrets_file, 'r')
    secrets = json.load(f)
    f.close()

    @app.route('/gconnect', methods=['POST'])
    def gconnect():

        if request.args.get('state') != login_session['state']:
            msg = 'Invalid state parameter'
            return gen_response(msg)

        # state token matches so we use the one time auth_code
        auth_code = request.data
        print auth_code
        try:
            # upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(secrets_file, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
                
        except FlowExchangeError:
            msg = 'Failed to upgrade the authorization code.'
            return gen_response(msg)

        # Check that the access token is valid.
        token = credentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        result = json.loads(httplib2.Http().request(url % token, 'GET')[1])
        print result
            
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            msg = result.get('error')
            return gen_response(msg, rc=500)

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            msg = "Token's user ID doesn't match given user ID."
            return gen_response(msg)

        if result['issued_to'] != secrets['web']['client_id']:
            msg = "Token's client ID does not match app_id."
            return gen_response(msg)

        # Check to see if user is already logged in
        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if (stored_credentials is not None) and (gplus_id == stored_gplus_id):
            msg = 'Current user is already connected.'
            return gen_response(msg, rc=200)

        # Store the access token in the session for later use.
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

        flash("you are now logged in as %s" % login_session['username'])
        return redirect('/conferences')


    # Logout - Revoke a current user's token and reset their login session
    #
    @app.route('/gdisconnect')
    def gdisconnect():

        credentials = login_session.get('credentials')
        if credentials is None:
            msg = 'Current user not connected.'
            return gen_response(msg)
    
        if True:
            print "credentials:\n", credentials

        access_token = credentials.access_token
        if True: 
            print "access_token:\n", access_token

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        result = httplib2.Http().request(url, 'GET')[0]
    
        if True:
            print "result:\n"
            for k in result:
                print "%s: %s" % (k, result[k])

        if result['status'] == '200':
            # Reset the user's login_session.
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']

            flash('Successfully disconnected.')
            return redirect('/conferences')

        else:
            # For whatever reason the given token was invalid.
            msg = 'Failed to revoke token for given user.'
            return gen_response(msg, rc=400)

