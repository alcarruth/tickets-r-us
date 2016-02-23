#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Flask libraries
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session

# OAuth2 client libraries
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Standard python libraries
import httplib2, json, requests, random, string

from tickets import User

DEBUG = True
LOG_ERRORS = True

# gen_response() is just a little wrapper around make_response()
# to make the code below more readable.
#
def gen_response(msg, rc=401, content_type='application/json'):
    if DEBUG or LOG_ERRORS:
        print msg
    response = make_response(json.dumps(msg), rc)
    response.headers['Content-Type'] = content_type
    return response


def auth_init(app, db_session):

    @app.route('/login')
    def login():

        state = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for x in xrange(32))
        if DEBUG:
            print state
        login_session['state'] = state
        #return render_template('login.html', STATE=state)
        return render_template('udacity_login.html', STATE=state)


    def createUser(login_session):
        user = User(
            name = login_session['username'],
            email = login_session['email'],
            picture = login_session['picture']
        )
        db_session.add(user)
        db_session.commit()
        return user.id

    def getUserInfo(user_id):
        user = db_session.query(User).filter_by(id=user_id).one()
        return user

    def getUserID(email):
        try:
            user = db_session.query(User).filter_by(email=email).one()
            return user.id
        except:
            return None


