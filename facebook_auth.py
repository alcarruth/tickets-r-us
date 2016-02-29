#!/usr/bin/python
# -*- coding: utf-8 -*-

# Standard python libraries
import json, httplib2, requests

# Flask libraries
from flask import request, redirect, flash, make_response
from flask import session as login_session

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

def facebook_auth(app, db_session):

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
        user_id = getUserID(db_session, login_session['email'])
        if not user_id:
            user_id = createUser(db_session, login_session)
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


    return (fbconnect, fbdisconnect)
