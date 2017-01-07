class RecorderException(Exception):
    pass

import pyaudio
import recording
import logging
import time

class Recorder(object):
    _CHUNK = 1024
    _RATE = 44100
    _CHANNELS = 1

    def __init__(self, cfg):
        
        self._config = cfg

        self._audio = pyaudio.PyAudio()

        self._FORMAT = self._audio.get_sample_size(pyaudio.paInt16)
        #self._input_idx = self._config.recorder.input_device_index
        #self._stream = self._audio.open(format=pyaudio.paInt16,
        #                                channels=self._CHANNELS,
        #                                rate=self._RATE,
        #                                input=True,
        #                                input_device_index=self._input_idx,
        #                                frames_per_buffer=self._CHUNK / 2,
        #                                start=False)

    def _open_stream(self):
        self._input_idx = self._config.recorder.input_device_index
        # Use a stream with no callback function in blocking mode
        self._stream = self._audio.open(format=pyaudio.paInt16,
                                        channels=self._CHANNELS,
                                        rate=self._RATE,
                                        input=True,
                                       # input_device_index=self._input_idx,
                                        frames_per_buffer=self._CHUNK / 2)

    def record(self, duration):
        tic = time.clock()

        # Use a stream with no callback function in blocking mode
        #self._stream = self._audio.open(format=pyaudio.paInt16,
        #                                channels=self._CHANNELS,
        #                                rate=self._RATE,
        #                                input=True,
        #                               # input_device_index=self._input_idx,
        #                                frames_per_buffer=self._CHUNK / 2)
        self._open_stream()

        logging.debug('Recorder: start recording (%ss)...' % duration )
        frames = []
        limit = int(self._RATE / self._CHUNK * duration)
        logging.debug('Recorder: start loop (%s Chunks)...' % limit )
        valid_data = True
        error_rate = 0
        loop_counter = 0
        max_error_rate = self._config.recorder.max_error_rate
        for i in range(0, limit):
            loop_counter += 1
            #logging.debug('Recorder: reading chunk (i: %s, loop_counter: %s)...' % (i,loop_counter) )
            try:
                data = self._stream.read(self._CHUNK,exception_on_overflow=False)
                frames.append(data)
            except IOError as error:
                error_rate += 1
                logging.debug('Recorder: IOError')
                #logging.debug('IOError (frame: %s, error_rate: %s, error: %s)...' % (i, error_rate, str(error)) )
                  
                if error_rate < max_error_rate:
                  logging.debug('Recorder: error_rate < %s: try to read again' % max_error_rate)
                  #logging.debug('stream (strem: %s)...' % (self._stream.__dict__) )
                  i = (i-1)
                  continue
                else:
                  logging.error('Recorder: error_rate is to high, cancel recording')
                  valid_data = False
                  break

        logging.debug('Recorder: end loop (after %s loops)...' % loop_counter)
              
        try:   
           self._stream.stop_stream()
        except IOError as error:
                logging.debug('Recorder: IOError while stop_stream operation')
                
        toc = time.clock()

        logging.debug('Recorder: end recording (time used: %ss)...' % (toc-tic) )
        rec = recording.Recording(b''.join(frames), self._RATE, self._FORMAT, self._CHANNELS)
 
        if valid_data:
         return rec
        else:
         return None


    def close(self):
        self._stream.close()
        self._audio.terminate()

    def __del__(self):
        try:
            self.close()
        except:
            pass
