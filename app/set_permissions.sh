#!/bin/sh

db_name='tickets'
db_owner='carruth'
db_user='catalog'

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

