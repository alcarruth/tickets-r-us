#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

#app_dir = '/opt/git/fullstack-p3-item-catalog/app/'
app_dir = '/opt/git/udacity/fullstack-projects/fullstack-p3-item-catalog/app/'

os.chdir(app_dir)
sys.path.insert(0, app_dir)

import settings

from tickets_web import app as application
