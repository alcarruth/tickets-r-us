#!/usr/bin/python
# -*- coding: utf-8 -*-

# must match setting in reset_db.sh 
db_name = 'tickets'

# db backend 
# either 'postgres' or 'sqlite' 
engine_type = 'sqlite'
#engine_type = 'postgres'

# options for dummy data creation
year = 2016
number_of_games = 11
number_of_users = 1000

# This is the number of ticket _lots_.
# The actual number of tickets created will 
# be 2 or 3 times this amount.
number_of_ticket_lots = 5000
