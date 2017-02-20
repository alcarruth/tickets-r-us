#!/bin/sh

# reset_db.sh

# Running this script will clean the database, both
# postgres and sqlite versions and then repopulate
# using the db's init script, e.g. init_tickets.py
# 

db_name='tickets'

# re-create the PostgreSQL database
psql -c "DROP DATABASE IF EXISTS ${db_name};"
psql -c "CREATE DATABASE ${db_name};"

# remove the SQLite db file
rm -v  "${db_name}.db" 2> /dev/null

# initialize database
python "init_${db_name}.py"
