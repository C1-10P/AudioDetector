#!/bin/bash
# http://raspberrypirecipes.blogspot.de/2014/02/raspberry-pi-using-pyaudio-external.html
sudo apt-get install git
git clone http://people.csail.mit.edu/hubert/git/pyaudio.git
sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get python-dev
sudo python pyaudio/setup.py install
