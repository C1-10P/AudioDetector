#!/bin/bash

CMD=${1}
DATE=${2}
APP_NAME="AudioDetector"

function show_help {
    echo "This is $APP_NAME."
    echo "Available options: "
    echo "start - To start $APP_NAME."
    echo "stop  - To stop $APP_NAME."
    echo "test  - To run tests"
    echo "train1 - To add fingerprints"
    echo "train2 - To add fingerprints"
    echo "graph - To display graph"
    echo "log   - To display debug log"
    echo "clean - Recompile python files and delte logfiles"
    echo "ouput - To display output log"
    echo "help  - to display this information"
}

function clean {
   cd audio_detector
   python2.7 -m compileall .
   cd tools
   rm add_finger_print.log
   cd ..
   rm audiodetector_output.log
   rm audiodetector.log
   cd ..
}


function start {
    cd audio_detector
    python2.7 -u audio_detector.py >> audiodetector_output.log 2>&1 &
    pid=$!
    PGID=$(ps -o pgid= $pid | grep -o [0-9]*)
    echo $PGID > app.pid
    cd ..
}

function stop {
    cd audio_detector
    pid=$(cat app.pid)
    kill -9 -$pid
    rm app.pid
    cd ..
}

function graph {
    cd audio_detector
    if [[ -z "$DATE" ]]; then
        python2.7 plot_occurences.py
    else
        python2.7 plot_occurences.py -d $DATE
    fi
    cd ..
}

function run_tests {
    # python2.7 -m unittest discover -p 'tests/*_tests.py'
}

function log {
    tailf audio_detector/audiodetector.log

}

function output {
    tailf audio_detector/audiodetector_output.log
}

function train1 {
    cd audio_detector/tools
    python2.7 add_finger_print.py -d ../../data/sample_data
    cd ..
    cd ..
}


function train2 {
    cd app/tools
    python2.7 add_finger_print.py -d ../../data/sample_data2
    cd ..
    cd ..
}


case $CMD in
    'start')
    start
    ;;
    'stop')
    stop
    ;;
    'graph')
    graph $GRAPH $DATE
    ;;
    'test')
    run_tests
    ;;
    'train')
    train1
    train2
    ;;
    'train1')
    train1
    ;;
    'train2')
    train2
    ;;
    'output')
    output
    ;;
    'log')
    log
    ;;
    'clean')
    clean
    ;;
    'help')
    show_help
    ;;
    *)
    show_help
esac
