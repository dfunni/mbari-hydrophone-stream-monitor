import pyaudio
import wave
import sys
import os
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import numpy as np
from pydub import AudioSegment
import requests
import time
import struct


def mbari_stream(filename, duration_s):
    stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'

    r = requests.get(stream_url, stream=True)
    print("recording")
    
    with open(filename, 'wb') as f:
        #t_end = time.time() + duration_s
        try:
            for block in r.iter_content(1024):
            #t = time.time()
            #if time.time() < t_end:
                f.write(block)
            #else:
            #    print("done recording")
            #    break
        except KeyboardInterrupt:
            pass


def mic_record(filename, time_s, rate=44100):

    chunk = 1024
    audio = pyaudio.PyAudio()

    # start recording
    stream = audio.open(format=pyaudio.paInt16,
                        channels=2,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    print("recording...")
    frames = []
    secs = [int(rate*l/chunk) for l in range(time_s)]
    
    for i in range(int(rate/chunk * time_s)):
        if i in secs:
            print(time_s - secs.index(i))
        data = stream.read(chunk)
        frames.append(data)

    print("finished recording")

    # stop recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(2)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()


def stream_spec(n=128, chunk=1024, fs=44100):
    mic = pyaudio.PyAudio()

    stream = mic.open(format=pyaudio.paInt16, 
                      channels=1, 
                      rate=fs, 
                      input=True, 
                      frames_per_buffer=1024)

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    def get_spectrum():
        data = stream.read(chunk, exception_on_overflow=False)
        data = np.frombuffer(data, dtype=np.int16())
        f, _, Sxx = signal.spectrogram(data, fs=fs, nfft=1024)
        return f, 10*np.log10(Sxx)

    _, Sxx = get_spectrum()
    h, w = Sxx.shape
    sxx = np.zeros((h, w*n))
    t = [*range(w*n)]

    while True:
        try:
            f, Sxx = get_spectrum()
            sxx[:, :w] = Sxx
            plt.clf()
            plt.pcolormesh(t, f, sxx, cmap='jet')
            plt.pause(0.001)
            sxx = np.roll(sxx, w, axis=1)
        except KeyboardInterrupt:
            break
        
    stream.stop_stream()
    stream.close()
    mic.terminate()


def plot_spectrogram(filename):
    fs, x = wavfile.read(filename)
    f, t, sxx0 = signal.spectrogram(x[:,0], fs, nfft=1024)  # channel 0
    f, t, sxx1 = signal.spectrogram(x[:,1], fs, nfft=1024)  # channel 1

    plt.subplot(211)
    #plt.pcolormesh(t, f, np.log10(sxx0), cmap='jet')
    plt.pcolormesh(t, f,np.log(sxx0), cmap='jet')

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.subplot(212)
    #plt.pcolormesh(t, f, np.log10(sxx1), cmap='jet')
    plt.pcolormesh(t, f, np.log(sxx1), cmap='jet')

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()
    
    return t, f, sxx0, sxx1


def mp3_to_wav(src, dst):
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format='wav')
    os.remove(src)


def play_wav(filename):
    chunk = 1024

    wf = wave.open(filename, 'rb')

    # instantiate PyAudio
    p = pyaudio.PyAudio()

    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(chunk)

    # play stream
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk)

    # stop stream
    p.terminate()




