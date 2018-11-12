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

# TODO: 
# where to put Login?
# do we really need it?
# maybe just use a dict.
# maybe define class Auth_Client and have both
# google_auth and facebook_auth sub-class it.


#------------------------------------------------------------------------------------
# Google+ Authorization Client

class Google_Auth_Client:

    def __init__(self, secrets_file):
        self.secrets_file = secrets_file
        f = open(secrets_file, 'r')
        self.client_id = json.load(f)['web']['client_id']
        f.close()
        self.oauth_flow = flow_from_clientsecrets(self.secrets_file, scope='')
        self.oauth_flow.redirect_uri = 'postmessage'

    def connect(self, auth_code, Login):

        credentials = self.oauth_flow.step2_exchange(auth_code)
        access_token = credentials.access_token,
        access_id = credentials.id_token['sub']

        # get access_data from access_token
        url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        access_data = json.loads(httplib2.Http().request(url % access_token, 'GET')[1])

        # If there was an error in the access token info, abort.
        error_msg = access_data.get('error')
        if error_msg is not None:
            msg = error_msg + ' bad access token'
            flash(msg)
            print >> sys.stderr, msg
            raise Exception(msg)

        # verify that the access token is used for the intended user.
        if access_data['user_id'] != access_id:
            msg = "Token's user ID doesn't match given user ID."
            flash(msg)
            print >> sys.stderr, msg
            raise Exception(msg)

        # check that token's client_id matches the app_id
        if access_data['issued_to'] != self.client_id:
            msg = "Token's client ID does not match app_id."
            flash(msg)
            print >> sys.stderr, msg
            raise Exception(msg)

        # Get user data
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)
        user_data = json.loads(answer.text)

        return Login('google', access_token, access_id, user_data)


    # Logout - Revoke a current user's token and reset their login session
    #
    def disconnect(self, login):

        access_token = login['access_token']
        if access_token == None:
            return None
        else:
            url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
            result = httplib2.Http().request(url, 'GET')[0]
            return result

