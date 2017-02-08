#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

app_dir = '/opt/git/tickets-r-us/app'
os.chdir(app_dir)
sys.path.insert(0, app_dir)

import settings

from tickets_web import app as application
