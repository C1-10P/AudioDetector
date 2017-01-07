import argparse
import os
import wave
import logging
# enable parent folder includes
# http://stackoverflow.com/questions/714063/importing-modules-from-parent-folder

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from analyze import analyzer
from storage import storage
from audio import recording
import config

def add_finger_print(file_path):
    
    a = analyzer.Analyzer()
    s = storage.Storage(config.Config("../config.json"))

    waveFile = wave.open(file_path)
    waveData = waveFile.readframes(waveFile.getnframes())

    rec = recording.Recording(waveData, waveFile.getframerate(), waveFile.getsampwidth(), waveFile.getnchannels())

    finger_print = a.finger_print(rec)
    finger_print.set_name(os.path.basename(file_path))

    s.add_finger_print(finger_print)

if __name__ == "__main__":

    logging.basicConfig(filename='add_finger_print.log', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="Path to wave file", dest="file")
    parser.add_argument("-d", "--dir", type=str, help="Path to folder with wave files", dest="dir")

    args = parser.parse_args()

    if args.dir is not None:
        wave_files = [os.path.join(args.dir, file_name) for file_name in os.listdir(args.dir) if file_name.endswith(".wav")]
    elif args.file is not None:
        wave_files = [args.file]
    else:
        parser.print_help()
        wave_files = []

    for wave_file in wave_files:
        print "Processing: " + wave_file
        add_finger_print(wave_file)
