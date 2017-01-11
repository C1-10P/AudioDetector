#!/bin/bash

CMD=${1}
DATE=${2}
APP_NAME="AudioDetector"

function show_help {
    echo "This is $APP_NAME."
    echo "Available options: "
    echo "alsa-start - To start $APP_NAME in alsa record mode."
    echo "pyaudio-start - To start $APP_NAME in pyaudio mode."
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


function clean_up {
        rm data/recording/signal_9s_1.wav
        rm data/recording/signal_9s_2.wav
        rm data/recording/signal_9s_3.wav
	# Perform program exit housekeeping
	echo "Good Bye."
	exit
}


function recording1(){
	echo "Start Recording 1 ..."
#	arecord -q -D plughw:1,0 -d 9 -f S16_LE -c1 -r44100 -t wav data/recording/signal_9s_1.wav
#  shitty Bug in arecord on raspberry creates a lot of wav-files
#  https://github.com/nodesign/weio/issues/178
#  http://superuser.com/questions/583826/recording-using-arecord-creates-thousands-of-files
#  Workaround:
        timeout 9s arecord -D plughw:1,0 -d 9 -f S16_LE -c 1 -r 44100 -t wav - > data/recording/signal_9s_1.wav 2> /dev/null
#        normalize-audio -q data/recording/signal_9s_1.wav 2> /dev/null

#        timeout 5s arecord -D plughw:1,0 -d 5 -f S16_LE -c 1 -r 22000 -t wav - > data/recording/signal_9s_1.wav 2> /dev/null

}

function recording2(){
        echo "Start Recording 2 ..."
#  arecord -q -D plughw:1,0 -d 9 -f S16_LE -c1 -r44100 -t wav data/recording/signal_9s_2.wav
#  shitty Bug in arecord on raspberry creates a lot of wav-files
#  https://github.com/nodesign/weio/issues/178
#  http://superuser.com/questions/583826/recording-using-arecord-creates-thousands-of-files
#  Workaround:

        timeout 9s arecord -D plughw:1,0 -d 9 -f S16_LE -c 1 -r 44100 -t wav - > data/recording/signal_9s_2.wav 2> /dev/null
#        normalize-audio -q data/recording/signal_9s_2.wav 2> /dev/null
#        timeout 5s arecord -D plughw:1,0 -d 5 -f S16_LE -c 1 -r 22000 -t wav - > data/recording/signal_9s_2.wav 2> /dev/null

}


function recording3(){
        echo "Start Recording 3 ..."
#  arecord -q -D plughw:1,0 -d 9 -f S16_LE -c1 -r44100 -t wav data/recording/signal_9s_2.wav
#  shitty Bug in arecord on raspberry creates a lot of wav-files
#  https://github.com/nodesign/weio/issues/178
#  http://superuser.com/questions/583826/recording-using-arecord-creates-thousands-of-files
#  Workaround:

        timeout 9s arecord -D plughw:1,0 -d 9 -f S16_LE -c 1 -r 44100 -t wav - > data/recording/signal_9s_3.wav 2> /dev/null
#        normalize-audio -q data/recording/signal_9s_3.wav 2> /dev/null
#        timeout 5s arecord -D plughw:1,0 -d 5 -f S16_LE -c 1 -r 22000 -t wav - > data/recording/signal_9s_3.wav 2> /dev/null

}


function analyse1() {

    cd audio_detector
    python2.7 -O -u audio_detector.py --file ../data/recording/signal_9s_1.wav >> audiodetector_output.log 2>&1 &
    cd ..


}

function analyse2() {

    cd audio_detector
    python2.7 -O -u audio_detector.py --file ../data/recording/signal_9s_2.wav >> audiodetector_output.log 2>&1 &
    cd ..
}

function analyse3() {

    cd audio_detector
    python2.7 -O -u audio_detector.py --file ../data/recording/signal_9s_3.wav >> audiodetector_output.log 2>&1 &
    cd ..
}


function start_alsa {

    trap clean_up SIGHUP SIGINT SIGTERM

    echo "stop programm by pressing STRG-C"
    echo ""
    while true; do

       recording1 

       analyse1 &

       recording2

       analyse2 &

       recording3

       analyse3 &

    done


}

function start_pyaudio {
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
    python2.7 -m unittest discover -p 'audio_detector/tests/*_tests.py'
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
    cd audio_detector/tools
    python2.7 add_finger_print.py -d ../../data/sample_data2
    cd ..
    cd ..
}


case $CMD in
    'alsa-start')
    start_alsa
    ;;
    'pyaudio-start')
    start_pyaudio
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
