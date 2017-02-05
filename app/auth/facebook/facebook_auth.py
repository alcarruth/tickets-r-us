#!/usr/bin/python
# -*- coding: utf-8 -*-

# See facebook developer console for Tickets'R'Us
# https://developers.facebook.com/apps/907786629329598/settings/

# Standard python libraries
import json, httplib2, requests, sys

# Flask libraries
from flask import request, redirect, flash, make_response

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import urllib
from urlparse import parse_qs

# TODO: 
# where to put Login?
# do we really need it?
# maybe just use a dict.
# maybe define class Auth_Client and have both
# google_auth and facebook_auth sub-class it.

#------------------------------------------------------------------------------------
# Facebook Authorization Client

class Facebook_Auth_Client:

    def __init__(self, secrets_file):
        self.secrets_file = secrets_file
        f = open(secrets_file, 'r')
        secrets = json.load(f)['web']
        f.close()
        self.access_token_url = 'https://graph.facebook.com/oauth/access_token'
        self.access_token_params = {
            'grant_type': 'fb_exchange_token',
            'client_id': secrets['app_id'],
            'client_secret': secrets['app_secret'],
            'fb_exchange_token': None }
        self.data_url = 'https://graph.facebook.com/v2.4/me'
        self.data_params = {
            'fields': 'name,id,email',
            'access_token': None }
        self.img_url = 'https://graph.facebook.com/v2.4/me/picture'
        self.img_params = {
            'redirect': 0, 
            'height': 200,
            'width': 200,
            'access_token': None }

    def connect(self, auth_code, Login):

        # we'll fill these in as we go
        user_data = {}

        # use auth_code to get access_token
        url = self.access_token_url
        params = self.access_token_params.copy()
        params['fb_exchange_token'] = auth_code
        response = requests.get(url, params=params)
        data = parse_qs(response.text)
        access_token = data['access_token'][0]

        # use access_token to get user's name and email
        url = self.data_url
        params = self.data_params.copy()
        params['access_token'] = access_token
        response = requests.get(url, params=params)
        data = response.json()
        access_id = data['id']
        user_data['name'] = data['name']
        user_data['email'] = data['email']

        # use access_token to get user's picture
        url = self.img_url
        params = self.img_params.copy()
        params['access_token'] = access_token
        response = requests.get(url, params=params)
        data = response.json()
        user_data['picture'] = data['data']['url']

        login = Login('facebook', access_token, access_id, user_data)
        return login

    def disconnect(self, login):
        access_id = login['access_id']
        access_token = login['access_token']
        url = 'https://graph.facebook.com/%s/permissions?' % access_id
        params = { 'access_token': access_token }
        response = requests.delete(url, params=params)
        print >> sys.stderr, 'disconnect status code: %s' % response.status_code
        return response.status_code


