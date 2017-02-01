#!/usr/bin/python
# -*- coding: utf-8 -*-

# See facebook developer console for Tickets'R'Us
# https://developers.facebook.com/apps/907786629329598/settings/

# Standard python libraries
import json, httplib2, requests

# Flask libraries
from flask import request, redirect, flash, make_response

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from tickets import createUser, getUserByEmail

#------------------------------------------------------------------------------------
# Facebook Authorization

fb_client_secrets_file = 'oauth/fb/fb_client_secrets.json'
f = open(fb_client_secrets_file, 'r')
fb_client_secrets = json.load(f)
f.close()

class Facebook_Auth:

    def __init__(self, db_session, app_session):
        self.db_session = db_session
        self.app_session = app_session

    def connect(self, session_id):

        if session_id != self.app_session['session_id']:
            response = make_response(json.dumps('Invalid session_id.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token = request.data

        app_id = fb_client_secrets['web']['app_id']
        app_secret = fb_client_secrets['web']['app_secret']

        url = 'https://graph.facebook.com/oauth/access_token?'
        url += 'grant_type=fb_exchange_token'
        url += '&client_id=%s' % app_id
        url += '&client_secret=%s' % app_secret
        url += '&fb_exchange_token=%s' % access_token

        
        # Use token to get user data
        token = httplib2.Http().request(url, 'GET')[1].split("&")[0]
        url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
        data = json.loads(httplib2.Http().request(url, 'GET')[1])

        self.app_session['provider'] = 'facebook'
        self.app_session['facebook_id'] = data["id"]

        user_data = {}
        user_data['name'] = data["name"]
        user_data['email'] = data["email"]

        # The token must be stored in the self.app_session in order to 
        # properly logout, let's strip out the information before 
        # the equals sign in our token
    
        stored_token = token.split("=")[1]
        self.app_session['access_token'] = stored_token
    
        # Get user picture
        url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
        data = json.loads(httplib2.Http().request(url, 'GET')[1])
        user_data['picture'] = data["data"]["url"]

        # see if user exists
        user = getUserByEmail(self.db_session, user_data['email'])
        if not user:
            user = createUser(self.db_session, user_data)
        self.app_session['user'] = user

        output = ''
        output += '<h1>Welcome, %s!</h1>' % user.name
        output += '<img src="%s"' % user.picture
        output += ' style = "width: 300px; height: 300px;border-radius: 150px;'
        output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

        flash("Now logged in as %s" % user.name)
        return output

    def disconnect(self):
        facebook_id = self.app_session['facebook_id']
        access_token = self.app_session['access_token']
        url = 'https://graph.facebook.com/%s/' % facebook_id
        url += 'permissions?access_token=%s' % access_token
        result = httplib2.Http().request(url, 'DELETE')[1]

