#!/bin/bash

HTTP_SERVER='python -m SimpleHTTPServer'
APP_DIR='/opt/github/tickets/app/'
IP_ADDR='127.0.0.1'

APP_DIR='/opt/github/tickets/app/'
RUN_DIR=${APP_DIR}/run/

UWSGI_PORT='8082'
UWSGI_LOG=${RUN_DIR}/uwsgi.log
UWSGI_ERR=${RUN_DIR}/uwsgi.err
UWSGI_PID=${RUN_DIR}/uwsgi.pid

STATIC_PORT='8083'
STATIC_LOG=${RUN_DIR}/static.log
STATIC_ERR=${RUN_DIR}/static.err
STATIC_PID=${RUN_DIR}/static.pid

function uwsgi_server {

    case ${1} in

        start)
            mkdir ${RUN_DIR} 2> /dev/null
            uwsgi --socket ${IP_ADDR}:${UWSGI_PORT} --protocol http --file tickets.wsgi >${UWSGI_LOG} 2>${UWSGI_ERR} &
            echo "$!" > ${UWSGI_PID};
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
