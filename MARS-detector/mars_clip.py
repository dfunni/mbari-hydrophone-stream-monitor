import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pydub import AudioSegment
from scipy.signal import spectrogram
import yaml


class MarsClip(object):

    def __init__(self, filename):
        with open("detector_config.yaml", "r") as f:
            self.config = yaml.safe_load(f.read())
        self.filename = filename
        self.directory = self.config['DATA_ROOT']
        self.filepath = self.directory + self.filename
        self.audio = AudioSegment.from_mp3(self.filepath)
        self.samples = np.array(self.audio.get_array_of_samples())[::2] # the samples are interleaved channel samples, channels are equal (mono)


    def get_spec_img(self):
        '''Calculate spectrogram using scipy.signal.spectrogram
        Returns:
            sxx: numpy array of spectrogram data
        '''
        f, t, sxx = spectrogram(self.samples, **self.config['spectrogram_params'])
        sxx = 10*np.log10(sxx[:180, 4:])
        return sxx, f, t
    
    def get_samples(self):
        return self.samples
    

    def get_filename(self):
        return self.filename
    

    def get_filepath(self):
        return self.filepath
    