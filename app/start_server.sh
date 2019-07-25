#!/bin/bash

HTTP_SERVER='python -m SimpleHTTPServer'
APP_DIR='/var/www/git/udacity/tickets/app/'

IP_ADDR='127.0.0.1'
DYNAMIC_PORT='8082'
STATIC_PORT=8083

RUN_DIR=${APP_DIR}/run
LOG_DIR="/var/log/alcarruth/"
PID_DIR="/var/run/alcarruth/"

LOG_FILE=${LOG_DIR}/tickets.log
ERR_FILE=${LOG_DIR}/tickets.err
PID_FILE=${PID_DIR}/tickets.pid

ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function start_server {
    uwsgi --socket ${IP_ADDR}:${DYNAMIC_PORT} --protocol http -w tickets >${LOG_FILE} 2>${ERR_FILE} & 
}

start_server
echo $! > ${PID_FILE};
