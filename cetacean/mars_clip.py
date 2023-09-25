import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pydub import AudioSegment
from scipy.signal import spectrogram
import yaml
import base64
from io import BytesIO


class MarsClip(object):

    def __init__(self, filename):
        with open("config.yaml", "r") as f:
            self.config = yaml.safe_load(f.read())
        self.filename = filename
        self.directory = self.config['data_path']
        self.filepath = self.directory + self.filename
        self.audio = AudioSegment.from_mp3(self.filepath)
        self.samples = np.array(self.audio.get_array_of_samples())[::2] # the samples are interleaved channel samples, channels are equal (mono)


    def get_spec_img(self):
            '''Calculate spectrogram using scipy.signal.spectrogram
            Returns:
                sxx: numpy array of spectrogram data
            '''
            f, t, sxx = spectrogram(self.samples, **self.config['spectrogram_params'])
            return 10*np.log10(sxx), f, t


    def get_spec_img_data(self):
        ''' Generate the figure without using pyplot 
        '''
        sxx, f, t = self.get_spec_img()
                
        fig = Figure()
        ax = fig.add_axes([0.1,0.35, 0.9, 0.65])
        ax.set_yscale("function", functions=(lambda x : abs(x)**.8, lambda x : abs(x)**(1/.8)))
        ax.set_ylim((0, self.config['spectrogram_params']['fs']//2))       
        ax.pcolormesh(t, f, sxx, cmap='jet')
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return data


    def plot_specgram(self):
        '''View spectrogram using matplotlib specgram function
        '''
        sxx, freqs, t, _ = plt.specgram(self.samples, NFFT=512, noverlap=0, cmap='jet')
        plt.show()
     

    def plot_spectrogram_img(self):
        sxx, f, t = self.get_spec_img()
        
        def forward(x):
            return abs(x)**.8

        def inverse(x):
            return abs(x)**(1/.8)
        
        plt.yscale("function", functions=(forward, inverse))
        plt.ylim((0, self.config['spectrogram_params']['fs']//2))       
        plt.pcolormesh(t, f, 10*np.log10(sxx), cmap='jet')
        plt.show()
    

    def get_filename(self):
        return self.filename
    

    def get_filepath(self):
        return self.filepath
    

    def play(self):
        return self.audio
    

    # def mv_whale(self):
    #     new_path = os.path.join("assets/data/whale/", self.filename)
    #     os.rename(self.filepath, new_path)
    #     self.filepath = new_path
    #     return self.filepath
        

    # def mv_nowhale(self):
    #     new_path = os.path.join("assets/data/no_whale/", self.filename)
    #     os.rename(self.filepath, new_path)
    #     self.filepath = new_path
    #     return self.filepath


    # def cp_interesiting(self):
    #     new_path = os.path.join("assets/data/interesting/", self.filename)
    #     os.rename(self.filepath, new_path)
    #     self.filepath = new_path
    #     return self.filepath