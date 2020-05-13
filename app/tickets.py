#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import sys, os
import settings

os.chdir(settings.app_dir)
sys.path.insert(0, settings.app_dir)

from tickets_web import app

if __name__ == '__main__':

    import readline
    import rlcompleter
    readline.parse_and_bind("tab: complete")


