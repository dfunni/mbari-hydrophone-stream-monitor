''' This file is largely depricated. I am leaving it here in the case that it might be useful for inference.
If so:
TODO: convert to using torch.transforms
'''

import numpy as np
from pydub import AudioSegment
from torchaudio.transforms import Spectrogram
import torchaudio
import yaml


class MarsClip(object):

    def __init__(self, filename):
        with open("detector_config.yaml", "r") as f:
            self.config = yaml.safe_load(f.read())
        self.filename = filename
        self.directory = self.config['DATA_ROOT']
        self.filepath = self.directory + self.filename
        self.audio = AudioSegment.from_mp3(self.filepath)
        self.samples, self.fs = torchaudio.load(self.filepath, normalize=True)
        self.samples = self.samples[::2]
        # self.samples = np.array(self.audio.get_array_of_samples())[::2] # the samples are interleaved channel samples, channels are equal (mono)


    def get_spec_img(self):
        '''Calculate spectrogram using scipy.signal.spectrogram
        Returns:
            sxx: numpy array of spectrogram data
        '''
        # f, t, sxx = spectrogram(self.samples, **self.config['spectrogram_params'])
        transform = Spectrogram(**self.config['torch_spectrogram_params'])
        sxx = transform(self.samples)
        sxx = 10*np.log10(sxx[:,:180, 5:])
        return sxx#, f, t
    
    def get_samples(self):
        return self.samples
    

    def get_filename(self):
        return self.filename
    

    def get_filepath(self):
        return self.filepath
    