#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Standard python libraries
import json, httplib2, requests

# Flask libraries
from flask import request, redirect, flash
from flask import session as login_session

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from tickets import createUser, getUserID

#------------------------------------------------------------------------------------
# Google+ Authorization

google_client_secrets_file = 'oauth/google/google_client_secrets.json'
f = open(google_client_secrets_file, 'r')
google_client_secrets = json.load(f)
f.close()

def google_auth(app, db_session):

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
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        result = json.loads(httplib2.Http().request(url % access_token, 'GET')[1])
            
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
        stored_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if (stored_token is not None) and (gplus_id == stored_gplus_id):
            msg = 'Current user is already connected.'
            return gen_response(msg, rc=200)

        # Store the access token in the session for later use.
        login_session['provider'] = 'google'
        login_session['access_token'] = access_token
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        login_session['username'] = data["name"]
        login_session['picture'] = data["picture"]
        login_session['email'] = data["email"]

        # see if user exists
        user_id = getUserID(db_session, login_session['email'])
        if not user_id:
            user_id = createUser(db_session, login_session)
        login_session['user_id'] = user_id

        flash("you are now logged in as %s" % login_session['username'])
        return redirect('/conferences')

    # Logout - Revoke a current user's token and reset their login session
    #
    def gdisconnect():

        access_token = login_session.get('access_token')
        if access_token is None:
            msg = 'Current user not connected.'
            return gen_response(msg)

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        result = httplib2.Http().request(url, 'GET')[0]

    return (gconnect, gdisconnect)
