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

from tickets import createUser, getUserID

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
        self.app_session['provider'] = 'facebook'
        self.app_session['username'] = data["name"]
        self.app_session['email'] = data["email"]
        self.app_session['facebook_id'] = data["id"]

        # The token must be stored in the self.app_session in order to 
        # properly logout, let's strip out the information before 
        # the equals sign in our token
    
        stored_token = token.split("=")[1]
        self.app_session['access_token'] = stored_token
    
        # Get user picture
        url = 'https://graph.facebook.com/v2.4/me/picture?'
        url += '%s&' % token
        url += 'redirect=0&'
        url += 'height=200&'
        url += 'width=200'

        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        self.app_session['picture'] = data["data"]["url"]

        # see if user exists
        user_id = getUserID(self.db_session, self.app_session['email'])
        if not user_id:
            user_id = createUser(self.db_session, self.app_session)
        self.app_session['user_id'] = user_id

        output = ''
        output += '<h1>Welcome, %s!</h1>' % self.app_session['username']
        output += '<img src="%s"' % self.app_session['picture']
        output += ' style = "width: 300px; height: 300px;border-radius: 150px;'
        output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

        flash("Now logged in as %s" % self.app_session['username'])
        return output

    def disconnect(self):

        facebook_id = self.app_session['facebook_id']
        access_token = self.app_session['access_token']
        url = 'https://graph.facebook.com/%s/' % facebook_id
        url += 'permissions?access_token=%s' % access_token

        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]

