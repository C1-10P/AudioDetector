import argparse
import datetime

# enable parent folder includes
# http://stackoverflow.com/questions/714063/importing-modules-from-parent-folder

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from audio import recorder
import config

def record(file_path, duration):
    cfg = config.Config("../config.json")
    r = recorder.Recorder(cfg)

    rec = r.record(duration)
    rec.save(file_path)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        type=str,
                        help="Path to new wave file",
                        dest="file",
                        default=str(datetime.datetime.now()) + ".wav")

    parser.add_argument("-t", "--time",
                        type=int,
                        help="Recording time",
                        dest="time",
                        default=3)

    args = parser.parse_args()

    record(args.file, args.time)
