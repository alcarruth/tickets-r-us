#!/bin/bash


PATH="/opt/node/bin:${PATH}"
HTTP_SERVER='/opt/node/bin/http-server'
APP_DIR='/home/carruth/git/tickets/app/'

# TODO: There are a couple of untracked dependencies.
# Add these to requirements.pip and the README.md
#
#  npm install -g http-server
#  pip install uwsgi
#

IP_ADDR='127.0.0.1'
DYNAMIC_PORT='8082'
STATIC_PORT='8083'

RUN_DIR=${APP_DIR}/run
ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function uwsgi_server {

    LOG_FILE=${RUN_DIR}/${FUNCNAME}.log
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid
        
    case ${1} in

        start)
            mkdir ${RUN_DIR} 2> /dev/null
            source ${ACTIVATE}
            nohup uwsgi --socket ${IP_ADDR}:${DYNAMIC_PORT} --protocol http -w tickets >${LOG_FILE} &
            echo $! > ${PID_FILE}
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

    LOG_FILE=${RUN_DIR}/${FUNCNAME}.log
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid

    case ${1} in

        start)
            pushd tickets_web/static/
            ${HTTP_SERVER} -p ${STATIC_PORT} >${LOG_FILE} &
            echo $! > ${PID_FILE}
            popd
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
