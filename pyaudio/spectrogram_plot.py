import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import numpy as np

from pydub import AudioSegment

fs, x = wavfile.read('file.wav')
# x = AudioSegment.from_file(file='/Users/dave/Documents/mystuff/stream.wav')
# x = np.array(x.split_to_mono()[0])
f, t, sxx0 = signal.spectrogram(x[:,0], fs)
f, t, sxx1 = signal.spectrogram(x[:,1], fs)

#print(sxx.shape)
plt.subplot(211)
plt.pcolormesh(np.log10(sxx0))
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.subplot(212)
plt.pcolormesh(np.log10(sxx1))
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()

