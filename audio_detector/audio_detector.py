import sys
#sys.path.insert(1,'/usr/lib/python2.7/dist-packages')
#sys.path.insert(1,'/usr/local/lib/python2.7/dist-packages/PyAudio-0.2.9-py2.7-linux-armv6l.egg')
#sys.path.insert(1,'/usr/lib/python2.7/plat-arm-linux-gnueabihf')
#print sys.path

import multiprocessing
from audio import recorder
from storage import storage
from analyze import analyzer
from notification import notifier
import Queue
from datetime import datetime
import logging
import time
import wave
import argparse
import os
from audio import recording

class AudioDetector(object):

    def __init__(self, cfg):

        #super(AudioDetector, self).__init__(*args)
        self._config = cfg

        self._analyzer = analyzer.Analyzer()
        self._notifier = notifier.Notifier(self._config)
        self._storage = storage.Storage(self._config)

        self._last_notification = None
  
        # check if empty fingerprint list
        if not self._storage.get_finger_prints():
          logging.error('no fingerprints found ... must exit')
          raise IOError

        

    def alternative_mode(self,file_path):

        waveFile = wave.open(file_path)
        waveData = waveFile.readframes(waveFile.getnframes())
        rec = recording.Recording(waveData, waveFile.getframerate(), waveFile.getsampwidth(), waveFile.getnchannels())
        
        logging.debug('alternative_mode: analyze wav file ...')
        finger_print = self._analyzer.finger_print(rec)
        logging.debug('alternative_mode: detection start ...')
        confidences = []
        finger_print_names = []
        #logging.debug('detecting_process: fingerprint %s ' % str(finger_print))
        for reference in self._storage.get_finger_prints():
          #logging.debug('detecting_process: compare %s ' % str(reference))
          if finger_print.compare(reference):
             confidences.append(finger_print.compare_confidence(reference))
             finger_print_names.append(reference.get_name())
             if confidences:
                logging.info('alternative_mode: <!> found confidences <!>')
                self._notify(confidences, finger_print_names)
        logging.debug('alternative_mode: detection end ...')



    def start(self):
        logging.debug('AudioDetector->start')
        self._recorder = recorder.Recorder(self._config)
        self._last_notification = None
        self._recording_process = None
        self._detecting_process = None
        self._processing_processes = None
        
        self._recording_queue = multiprocessing.Queue()
        self._finger_print_queue = multiprocessing.Queue()

	self._recording_alive = multiprocessing.Event()
	self._exit_group0 = multiprocessing.Event()
        self._exit_group1 = multiprocessing.Event()


        self.start_group0()
        self.start_group1()
        
        # watchdog is no multiprocessing process
        # https://docs.python.org/2/library/multiprocessing.html#multiprocessing.Process.terminate
        # Note that the start(), join(), is_alive(), terminate()
        # and exitcode methods should only be called by the process
        # that created the process object.
        self._watchdog()

        #self._recorder.close()

    def create_group0(self):
        logging.debug('AudioDetector->create_group0')

        #http://stackoverflow.com/a/37462587
        # nested if construct to prevent
        # 'NoneType' object has no attribute 'is_alive'
        create = True
        if (self._recording_process is not None):
          if (self._recording_process.is_alive()):
            create = False
      
        if create:
          self._recording_process = multiprocessing.Process(target=lambda: self._loop_group_0(self._recording))
        else:
          logging.error('assertion error: cancel creation of recording process') 

    def start_group0(self):
        logging.debug('AudioDetector->start_group0')
        self._exit_group0.clear()
        self.create_group0()
        self._recording_process.start()

    def create_group1(self):

        # nested if construct to prevent
        # 'NoneType' object has no attribute 'is_alive'
        create_detect = True
        if (self._detecting_process is not None):
          if (self._detecting_process.is_alive()):
            create_detect = False
 
        if create_detect:
           self._detecting_process = multiprocessing.Process(target=lambda: self._loop_group_1(self._detecting))
        else:
          logging.error('assertion error: cancel creation of detecting process') 

        # nested if construct to prevent
        # 'NoneType' object has no attribute 'is_alive'
        create_processing = True
        if (self._processing_processes is not None):
          # http://legacy.python.org/dev/peps/pep-0008/#programming-recommendations
          # Use the fact that empty sequences are false.
          if not self._processing_processes:
            for p in self._processing_processes:
              if p.is_alive():
                create_processing = False

        if create_processing: 
         self._processing_processes = []
         for i in range(2):
            self._processing_processes.append(multiprocessing.Process(target=lambda: self._loop_group_1(self._processing)))
        else:
         logging.error('assertion error: cancel creation of processing processes') 


    def start_group1(self):
        logging.debug('AudioDetector->start_group1')
        self._exit_group1.clear()
	self.create_group1()

        self._detecting_process.start()
        [p.start() for p in self._processing_processes]

        #self._recording_process.join()
        #logging.debug('AudioDetector->start#join1')
        #self._detecting_process.join()
        #logging.debug('AudioDetector->start#join2')
        #[p.join() for p in self._processing_processes]
        #logging.debug('AudioDetector->start#join3')
        

    def stop_group0(self):
        logging.debug('AudioDetector->stop_group0')
        self._exit_group0.set()
        if self._recording_process != None:
         self._recording_process.terminate()

    def stop_group1(self):
        logging.debug('AudioDetector->stop_group1')
        self._exit_group1.set()       

        if self._detecting_process != None:
         self._detecting_process.terminate()

        for p in self._processing_processes:
         if p != None: 
          p.terminate() 

    def stop(self):
        logging.debug('AudioDetector->stop')
        self.stop_group0()
        self.stop_group1()
        self._recorder.close()
     
    def _loop_group_0(self, func):
        while not self._exit_group0.is_set():
            func()

    def _loop_group_1(self, func):
        while not self._exit_group1.is_set():
            func()

    # sometimes the recording thread fails and needs a restart
    def _watchdog(self):
        watchdog_wait_time = self._config.audio_detector.watchdog_lookup_time
        self._recording_alive.clear()
        while True:
         logging.debug('watchdog: sleeping for %s s ...' % watchdog_wait_time)
         time.sleep(watchdog_wait_time) 
	 if self._recording_alive.is_set():
           logging.debug('watchdog: recording is alive')
           self._recording_alive.clear()
         else:
           logging.error('watchdog: recording is not alive')
           logging.info('watchdog: recording try to terminate and restart ...')
           self.stop_group0()
           restart_wait_time = self._config.audio_detector.watchdog_restart_wait
           logging.info('watchdog: recording terminated ... wating %s s before start' % restart_wait_time)
           time.sleep(restart_wait_time)
           self.start_group0()
           # time hardcorded
           time.sleep(5)
           if self._recording_alive.is_set():
              logging.info('watchdog: recording successfuly restarted')
           else:
              logging.error('watchdog: recording could not be restarted')
               

    def _recording(self):
        logging.debug('recording_process: trigger recording ...')
        rec = self._recorder.record(self._config.recorder.record_time)
        if rec != None:
          logging.debug('recording_process: put recording in recording queue ...')
          self._recording_queue.put(rec)

        logging.debug('recording_process: end recording ...')
        self._recording_alive.set()

    def _processing(self):
        try:
            rec = self._recording_queue.get(timeout=0.2)
            logging.debug('processing_process: got recording from recording queue ...')
        except Queue.Empty:
            pass
        else:
            logging.debug('processing_process: analyze and save to fingerprint queue ...')
            finger_print = self._analyzer.finger_print(rec)
            self._finger_print_queue.put(finger_print)
        


    def _detecting(self):
        
        try:
            finger_print = self._finger_print_queue.get(timeout=0.2)
            logging.debug('detecting_process: got fingerprint from fingerprint queue ...')
        except Queue.Empty:
            pass
        else:
            logging.debug('detecting_process: detection start ...')
            confidences = []
            finger_print_names = []
            #logging.debug('detecting_process: fingerprint %s ' % str(finger_print))
            for reference in self._storage.get_finger_prints():
                #logging.debug('detecting_process: compare %s ' % str(reference))
                if finger_print.compare(reference):
                    confidences.append(finger_print.compare_confidence(reference))
                    finger_print_names.append(reference.get_name())
            logging.debug('detecting_process: detection end ...')
            if confidences:
                logging.info('detecting_process: <!> found confidences <!>')
                self._notify(confidences, finger_print_names)
            

    def _notify(self, confidences, finger_print_names):

        now = datetime.now()
        self._storage.add_occurence(now, max(confidences))
        contents = self._format_occurences(now, confidences, finger_print_names)
        self._print_occurences(contents)
        
        send_notify = True
        if self._last_notification is not None:
          if not (now - self._last_notification).total_seconds() > self._config.email.notification_wait_time:
             send_notify = False

        if send_notify:
            self._last_notification = now
            self._notifier.notify(contents)

    def _format_occurences(self, now, confidences, finger_print_names):
        contents = "Found !\nTime: {}\n\n".format(str(now))

        for i in range(len(confidences)):
            contents += "Confidence: {:.2f} % Finger print name: {:s}\n".format(confidences[i], finger_print_names[i])
        logging.info(contents)
        return contents

    def _print_occurences(self, contents):
        print "###############################"
        print contents


if __name__ == "__main__":
    import config
    import logging

    cfg = config.Config("config.json")
    loglevel = getattr(logging, cfg.audio_detector.loglevel, logging.ERROR)
    
    #http://stackoverflow.com/a/23874319
    logging.basicConfig(filename='audiodetector.log', 
level=loglevel, format="%(asctime)s;%(levelname)s;%(message)s")

    logging.info('Start')
    

    parser = argparse.ArgumentParser()
    parser.add_argument('--file',help='put the path to a wav-file here. the programm will start in alternative mode.',
                        default=None)
    parser.add_argument('-q', dest='quiet', action='store_true', default=False)


    # Arguments
    args = parser.parse_args()
    file_path = args.file

    alternative_mode = False
    if file_path is not None:
     alternative_mode = True
 
    quiet = args.quiet

    b = AudioDetector(cfg)
    if alternative_mode:
      b.alternative_mode(file_path)
    else:
      b.start()

    logging.info('END')


    
