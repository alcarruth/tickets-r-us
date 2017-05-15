#!/bin/bash

APP_DIR='/opt/git/udacity/fullstack-projects/fullstack-p3-item-catalog/app/'
IP_ADDR='192.168.166.230'
DYNAMIC_PORT='8082'
STATIC_PORT='8083'

RUN_DIR=${APP_DIR}/run
ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function tickets_uwsgi_server {

    LOG_FILE=${RUN_DIR}/${FUNCNAME}.log
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid
        
    case ${1} in

        start) 
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

 
function tickets_static_server {

    LOG_FILE=${RUN_DIR}/${FUNCNAME}.log
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid

    case ${1} in

        start)
            pushd tickets_web/static/
            http-server -p ${STATIC_PORT} >${LOG_FILE} &
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

