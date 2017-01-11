import numpy as np
import fingerprint
from numpy import fft
import logging
from operator import itemgetter

class Analyzer(object):

    def finger_print(self, recording):

        logging.debug("Analyzer->fingerprint start")

        if recording.data_format() == 2:
            data_type = np.int16
        else:
            raise Exception("Wrong data format!" + str(recording.format()))
        audio_data = np.fromstring(recording.data(), dtype=data_type)
        logging.debug("Analyzer->fingerprint step 1")
        freq, amp = self._fft(audio_data)
        logging.debug("Analyzer->fingerprint step 2")
        fp =  fingerprint.FingerPrint(self._generate_print(freq, amp))
        logging.debug("Analyzer->fingerprint end")

        return fp

    def _fft(self, audio_data):


        amp = fft.rfft(audio_data)
        freq = fft.fftfreq(audio_data.shape[-1])[:len(amp)]

        return freq, amp.real

    def _generate_print(self, freq, amp):
        logging.debug("Analyzer->_generate_print step 1")
        data = zip(freq, amp)
        logging.debug("Analyzer->_generate_print step 2")
        # data.sort(key=lambda x: x[1], reverse=True)
        # faster
        # http://stackoverflow.com/a/20183124
        data.sort(key=itemgetter(1), reverse=True)
        logging.debug("Analyzer->_generate_print step 3")
        return data[:100]
