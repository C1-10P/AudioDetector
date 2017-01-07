import argparse
import os

import logging
# enable parent folder includes
# http://stackoverflow.com/questions/714063/importing-modules-from-parent-folder

import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from notification import emailmessage
import config

def email(test_string):
    
    cfg = config.Config("../config.json")

    email = emailmessage.EmailMessage(cfg)
    email.contents(test_string)
    email.send()

if __name__ == "__main__":

    logging.basicConfig(filename='add_finger_print.log', level=logging.DEBUG)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test-string", type=str, help="test email string", dest="test_string", default="test test test")

    args = parser.parse_args()
    email(args.test_string)
