#!/bin/sh

# reset_db.sh

# Running this script will clean the database, both
# postgres and sqlite versions and then repopulate
# using the db's init script, e.g. init_tickets.py
# 

db_name='tickets'
db_owner='carruth'
db_user='catalog'

# these must be done as postgres super user.
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ${db_name};"
sudo -u postgres psql -c "DROP ROLE IF EXISTS ${db_user};"
sudo -u postgres psql -c "DROP ROLE IF EXISTS ${db_owner};"
sudo -u postgres psql -c "CREATE USER ${db_owner} CREATEDB CREATEROLE;"
sudo -u postgres psql -c "CREATE DATABASE ${db_owner};"

# now we can do the rest as db_owner.
sudo -u ${db_owner} psql -c "CREATE USER ${db_user};"

# re-create the PostgreSQL database
sudo -u ${db_owner} psql -c "CREATE DATABASE ${db_name};"

# TODO:
# Should this be here? Everything else in here is postgresql.
# Maybe a separate script to reset SQLite db?
#
# remove the SQLite db file if it exists
rm -v  "${db_name}.db" 2> /dev/null

# initialize database
python "init_${db_name}.py"

# set db user permissions
sudo -u ${db_owner} psql ${db_name} -c \
    "GRANT SELECT on
     conference, game, game_id_seq
     to ${db_user};" ;

sudo -u ${db_owner} psql ${db_name} -c \
    "GRANT SELECT, UPDATE, INSERT, DELETE on
     ticket, ticket_lot, ticket_user
     to ${db_user};" ;

sudo -u ${db_owner} psql ${db_name} -c \
    "GRANT SELECT, UPDATE on
     team, team_id_seq,
     ticket_id_seq, ticket_lot_id_seq, ticket_user_id_seq
     to ${db_user};" ;

sudo -u ${db_owner} psql ${db_name} -c '\dp' ;

