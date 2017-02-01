#!/usr/bin/python
# -*- coding: utf-8 -*-

# See google developer console for Tickets'R'Us
# https://console.cloud.google.com/apis/credentials?project=tickets-r-us
 
# Standard python libraries
import json, httplib2, requests, sys

# Flask libraries
from flask import request, redirect, flash

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from tickets import createUser, getUserID

#------------------------------------------------------------------------------------
# Google+ Authorization

class Google_Auth:

    def __init__(self, db_session, app_session, secrets_file):
        self.db_session = db_session
        self.app_session = app_session
        self.secrets_file = secrets_file
        f = open(secrets_file, 'r')
        self.client_secrets = json.load(f)
        f.close()

    def app_id(self):
        return self.client_secrets['web']['client_id']

    def connect(self, session_id):

        print >> sys.stderr, "connecting via google"


        # verify session_id
        if session_id != self.app_session['session_id']:
            msg = 'Invalid session_id.'
            print >> sys.stderr, msg
            return gen_response(msg)
        print >> sys.stderr, "session_id ok"


        # get auth_code
        auth_code = request.data
        print >> sys.stderr, "auth_code: %s" % auth_code


        # get credentials
        try:
            oauth_flow = flow_from_clientsecrets(self.secrets_file, scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            msg = 'Failed to upgrade the authorization code.'
            print >> sys.stderr, msg
            return gen_response(msg)
        print >> sys.stderr, "credentials: %s" % str(credentials)


        # check access token
        access_token = credentials.access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        result = json.loads(httplib2.Http().request(url % access_token, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            msg = result.get('error') + ' bad access token'
            print >> sys.stderr, msg
            return gen_response(msg, rc=500)
        print >> sys.stderr, "access token good"


        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            msg = "Token's user ID doesn't match given user ID."
            print >> sys.stderr, msg
            return gen_response(msg)
        print >> sys.stderr, "access token is used for the intended user"


        # check that token's client_id matches the app_id
        if result['issued_to'] != self.client_secrets['web']['client_id']:
            msg = "Token's client ID does not match app_id."
            print >> sys.stderr, msg
            return gen_response(msg)
        print >> sys.stderr, "Token's client ID matches app_id."


        # Check to see if user is already logged in
        stored_token = self.app_session.get('access_token')
        stored_gplus_id = self.app_session.get('gplus_id')
        if (stored_token is not None) and (gplus_id == stored_gplus_id):
            msg = 'Current user is already connected.'
            print >> sys.stderr, msg
            return gen_response(msg, rc=200)
        print >> sys.stderr, "user is not already logged in"


        # Store the access token in the session for later use.
        self.app_session['provider'] = 'google'
        self.app_session['access_token'] = access_token
        self.app_session['gplus_id'] = gplus_id


        # Get user info
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        data = json.loads(answer.text)
        print >> sys.stderr, "got user info"


        # create user if new
        user_id = getUserID(self.db_session, data['email'])
        if not user_id:
            user_id = createUser(self.db_session, self.app_session)
            print >> sys.stderr, 'creating user ' + user_id


        self.app_session['user_id'] = user_id
        self.app_session['username'] = data["name"]
        self.app_session['picture'] = data["picture"]
        self.app_session['email'] = data["email"]

        print >> sys.stderr, "almost done"

        username = self.app_session['username']
        flash("you are now logged in as %s" % username)
        print >> sys.stderr, 'login successful for user %s' % username
        return redirect('/tickets/conferences')

    # Logout - Revoke a current user's token and reset their login session
    #
    def disconnect(self):

        access_token = self.app_session.get('access_token')
        if access_token is None:
            msg = 'Current user not connected.'
            return gen_response(msg)

        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        result = httplib2.Http().request(url, 'GET')[0]

