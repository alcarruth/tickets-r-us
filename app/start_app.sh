#!/bin/bash

HTTP_SERVER='python -m SimpleHTTPServer'
IP_ADDR='127.0.0.1'

APP_DIR='/opt/github/tickets/app/'
RUN_DIR=${APP_DIR}/run/
LOG_DIR="/var/log/alcarruth/tickets/"
PID_DIR="/var/run/alcarruth/tickets/"

UWSGI_PORT='8082'
UWSGI_LOG=${LOG_DIR}/uwsgi.log
UWSGI_ERR=${LOG_DIR}/uwsgi.err
UWSGI_PID=${PID_DIR}/uwsgi.pid

STATIC_PORT='8083'
STATIC_LOG=${LOG_DIR}/static.log
STATIC_ERR=${LOG_DIR}/static.err
STATIC_PID=${PID_DIR}/static.pid

#ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function uwsgi_server {

    case ${1} in

        start)
            mkdir ${RUN_DIR} 2> /dev/null
            #source ${ACTIVATE}
            uwsgi --socket ${IP_ADDR}:${UWSGI_PORT} --protocol http -w tickets >${UWSGI_LOG} 2>${UWSGI_ERR} &
            echo "$!" > ${UWSGI_PID};
            #start_server
            #deactivate
            ;;

        stop)
            pid=$(cat ${UWSGI_PID})
            kill ${pid}
            rm ${UWSGI_PID}
            ;;

        restart)
            ${FUNCNAME} stop
            ${FUNCNAME} start
            ;;

        clear)
            echo > ${UWSGI_LOG}
            ;;
        
        *)
            echo "usage: ${FUNCNAME} [start|stop|restart|clear]"
            ;;

    esac;
}

 
function static_server {

    case ${1} in

        start)
            pushd tickets_web/static/ >/dev/null
            ${HTTP_SERVER} ${STATIC_PORT} >${STATIC_LOG} 2>${STATIC_ERR}&
            echo $! > ${STATIC_PID}
            popd >/dev/null
            ;;

        stop)
            pid=$(cat ${STATIC_PID})
            kill ${pid}
            rm ${STATIC_PID}
            ;;

        restart)
            ${FUNCNAME} stop
            ${FUNCNAME} start
            ;;

        clear)
            echo > ${STATIC_LOG}
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
