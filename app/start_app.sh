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
STATIC_PID_FILE=${PID_DIR}/tickets_static.pid

ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function start_server {
    uwsgi --socket ${IP_ADDR}:${DYNAMIC_PORT} --protocol http -w tickets >${LOG_FILE} 2>${ERR_FILE} &
    echo "$!" > ${PID_FILE};
}

function uwsgi_server {

    case ${1} in

        start)
            mkdir ${RUN_DIR} 2> /dev/null
            source ${ACTIVATE}
            uwsgi --socket ${IP_ADDR}:${DYNAMIC_PORT} --protocol http -w tickets >${LOG_FILE} 2>${ERR_FILE} &
            echo "$!" > ${PID_FILE};
            #start_server
            deactivate
            ;;

        stop)
            pid=$(cat ${PID_FILE})
            kill ${pid}
            rm ${PID_FILE}
            ;;

        restart)
            ${FUNCNAME} stop
            ${FUNCNAME} start
            ;;

        clear)
            echo > ${LOG_FILE}
            ;;
        
        *)
            echo "usage: ${FUNCNAME} [start|stop|restart|clear]"
            ;;

    esac;
}

 
function static_server {

    case ${1} in

        start)
            pushd tickets_web/static/
            ${HTTP_SERVER} ${STATIC_PORT} >${LOG_FILE} 2>${ERR_FILE}&
            echo $! > ${STATIC_PID_FILE}
            popd
            ;;

        stop)
            pid=$(cat ${STATIC_PID_FILE})
            kill ${pid}
            rm ${STATIC_PID_FILE}
            ;;

        restart)
            ${FUNCNAME} stop
            ${FUNCNAME} start
            ;;

        clear)
            echo > ${LOG_FILE}
            ;;
        
        *)
            echo "usage: ${FUNCNAME} [start|stop|restart|clear]"
            ;;

    esac;
}

case ${1} in

    start|stop|restart|clear)
        cd ${APP_DIR}
        uwsgi_server ${1}
        static_server ${1}
        ;;
        
    *)
        echo "usage: ${0} [start|stop|restart|clear]"
        ;;

esac;
