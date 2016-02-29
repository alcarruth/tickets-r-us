#!/usr/bin/python
# -*- coding: utf-8 -*-

from tickets import User
 
# add a user to the database
#
def createUser(db_session, login_session):
    user = User(
        name = login_session['username'],
        email = login_session['email'],
        picture = login_session['picture']
    )
    db_session.add(user)
    db_session.commit()
    return user.id

# maps a user_id to a user
#
def getUserInfo(db_session, user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user

# lookup a user by their email address
# and return the user id
#
def getUserID(db_session, email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

