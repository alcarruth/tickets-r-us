#!/bin/bash

HTTP_SERVER='python -m SimpleHTTPServer'
APP_DIR='/opt/github/tickets/app/'

IP_ADDR='127.0.0.1'
DYNAMIC_PORT='8082'
STATIC_PORT=8083

RUN_DIR=${APP_DIR}/run
#ACTIVATE=${APP_DIR}/tickets_venv/bin/activate

function uwsgi_server {

    LOG_FILE=${RUN_DIR}/${FUNCNAME}.log
    ERR_FILE=${RUN_DIR}/${FUNCNAME}.err
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid
        
    case ${1} in

        start)
            mkdir ${RUN_DIR} 2> /dev/null
            #source ${ACTIVATE}
            nohup uwsgi --socket ${IP_ADDR}:${DYNAMIC_PORT} --protocol http -w tickets >${LOG_FILE} 2>${ERR_FILE} &
            echo $! > ${PID_FILE}
            #deactivate
            ;;

        stop)
            pid=$(cat ${PID_FILE})
            kill ${pid}
            #rm ${PID_FILE}
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
    ERR_FILE=${RUN_DIR}/${FUNCNAME}.err
    PID_FILE=${RUN_DIR}/${FUNCNAME}.pid

    case ${1} in

        start)
            pushd tickets_web/static/
            ${HTTP_SERVER} ${STATIC_PORT} >${LOG_FILE} 2>${ERR_FILE}&
            echo $! > ${PID_FILE}
            popd
            ;;

        stop)
            pid=$(cat ${PID_FILE})
            kill ${pid}
            #rm ${PID_FILE}
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
