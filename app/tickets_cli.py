#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import sys, os
import settings

os.chdir(settings.app_dir)
sys.path.insert(0, settings.app_dir)

from tickets_db import *

if __name__ == '__main__':

    import readline
    import rlcompleter
    readline.parse_and_bind("tab: complete")

    print startup_info

    session = DBSession()
    conferences = session.query(Conference).all()
    tickets = session.query(Ticket).all()
    games = session.query(Game).all()
    users = session.query(User).all()
    teams = session.query(Team).all()

    
