#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# See google developer console for Tickets'R'Us
# https://console.cloud.google.com/apis/credentials?project=tickets-r-us
 
# Standard python libraries
import json, httplib2, requests

# Flask libraries
from flask import request, redirect, flash

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from tickets import createUser, getUserID

#------------------------------------------------------------------------------------
# Google+ Authorization

#google_client_secrets_file = 'oauth/google/linode-01_secrets.json'
google_client_secrets_file = 'oauth/google/zeus_client_secrets.json'
#google_client_secrets_file = 'oauth/google/localhost_5000_secrets.json'

f = open(google_client_secrets_file, 'r')
google_client_secrets = json.load(f)
f.close()

class Google_Auth:

    def __init__(self, db_session, login_session):
        self.db_session = db_session
        self.login_session = login_session

    def connect(self, state):

        if state != self.login_session['state']:
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
            msg = result.get('error') + ' bad access token'
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
        stored_token = self.login_session.get('access_token')
        stored_gplus_id = self.login_session.get('gplus_id')
        if (stored_token is not None) and (gplus_id == stored_gplus_id):
            msg = 'Current user is already connected.'
            return gen_response(msg, rc=200)

        # Store the access token in the session for later use.
        self.login_session['provider'] = 'google'
        self.login_session['access_token'] = access_token
        self.login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)

        self.login_session['username'] = data["name"]
        self.login_session['picture'] = data["picture"]
        self.login_session['email'] = data["email"]

        # see if user exists
        user_id = getUserID(self.db_session, self.login_session['email'])
        if not user_id:
            user_id = createUser(self.db_session, self.login_session)
        self.login_session['user_id'] = user_id

        flash("you are now logged in as %s" % self.login_session['username'])
        return redirect('/tickets/conferences')

    # Logout - Revoke a current user's token and reset their login session
    #
    def disconnect(self):

        access_token = self.login_session.get('access_token')
        if access_token is None:
            msg = 'Current user not connected.'
            return gen_response(msg)

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        result = httplib2.Http().request(url, 'GET')[0]

