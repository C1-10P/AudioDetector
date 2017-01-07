import os
import cPickle
import logging

class Storage(object):

    def __init__(self, config):
        self.config = config
        self._finger_print_db = self._load(self.config.storage.finger_print_db)
        logging.debug('_finger_print_db: %s ; %s' % (dir(self._finger_print_db),self._finger_print_db))
        self._occurence_db = self._load(self.config.storage.occurence_db)

    def add_finger_print(self, finger_print):
        self._finger_print_db.append(finger_print)
        logging.debug('add_finger_print: %s' % self._finger_print_db)
        self._save(self.config.storage.finger_print_db, self._finger_print_db)

    def get_finger_prints(self):
        return self._finger_print_db

    def add_occurence(self, time, confidence):
        self._occurence_db.append((time, confidence))
        self._save(self.config.storage.occurence_db, self._occurence_db)

    def get_occurences(self):
        return self._occurence_db

    def _load(self, file_path):


        if os.path.isfile(file_path):
            with open(file_path, 'rb') as fp:
                return cPickle.load(fp)
        else:
            logging.error('no finger printdb found (path: %s)' % file_path)
            return []

    def _save(self, file_path, db):

        with open(file_path, 'wb') as fp:
            cPickle.dump(db, fp)
