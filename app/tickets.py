#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

# TODO: unify app_dir setting
# shared with settings.py, start_app.sh, others?
app_dir = '/home/carruth/git/tickets-r-us/app/'

os.chdir(app_dir)
sys.path.insert(0, app_dir)

import settings

from tickets_web import app as application
