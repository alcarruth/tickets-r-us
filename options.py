#!/usr/bin/python
# -*- coding: utf-8 -*-

# must match setting in reset_db.sh 
db_name = 'tickets'

# db backend 
# either 'postgres' or 'sqlite' 
engine_type = 'postgres'

# options for dummy data creation
year = 2016
number_of_games = 11
number_of_users = 1000
number_of_ticket_lots = 10000
