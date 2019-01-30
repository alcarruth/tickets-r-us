#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
import settings

os.chdir(settings.app_dir)
sys.path.insert(0, settings.app_dir)

from tickets_web import app as application
