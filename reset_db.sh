#!/bin/sh

db_name="catalog"

# re-create the PostgreSQL database
psql -c "DROP DATABASE IF EXISTS ${db_name};"
psql -c "CREATE DATABASE ${db_name};"

# remove the SQLite db file
rm -v  "${db_name}.db" 2> /dev/null

# initialize database
python "init_${db_name}.py"

