#!/bin/bash

sudo apt-get install -y libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get install -y python-dev
sudo apt-get install -y python-matplotlib

sudo python setup.py install

