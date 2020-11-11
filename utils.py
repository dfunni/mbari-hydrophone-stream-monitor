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
from scipy import fft
from sklearn.preprocessing import minmax_scale


def mbari_stream(filename, duration):
    stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'

    r = requests.get(stream_url, stream=True)
    print(f'Recording for {duration}s.\nPress ctrl-C to stop recording.')

    with open(filename, 'wb') as f:
        t0 = time.time()

        for block in r.iter_content(1024):
            if (time.time() - t0) < duration:

                try:
                    f.write(block)

                except KeyboardInterrupt:
                    break
            else:
                break

def mbari_raw(n=128, chunk=1024, fs=44100):
    stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'
    r = requests.get(stream_url, stream=True)

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    def get_spectrum(block):
        block = np.frombuffer(block, dtype=np.int16())
        f, _, Sxx = signal.spectrogram(block, fs=fs, nfft=chunk)
        return f, 10*np.log10(Sxx)
    
    # block = r.raw.read(chunk)
    # block = np.frombuffer(block, dtype=np.int16())

    while True:
        try:
            for block in r.iter_content(chunk):
                block = np.frombuffer(block, dtype=np.int16())
                plt.clf()
                plt.plot(block)
                plt.pause(0.001)
        except KeyboardInterrupt:
            break


def mbari_fft(n=128, chunk=1024, fs=44100):
    stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'
    r = requests.get(stream_url, stream=True)

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    def get_spectrum(block):
        block = np.frombuffer(block, dtype=np.int16())
        f, _, Sxx = signal.spectrogram(block, fs=fs, nfft=chunk)
        return f, 10*np.log10(Sxx)
    
    # block = r.raw.read(chunk)
    # block = np.frombuffer(block, dtype=np.int16())

    while True:
        try:
            for block in r.iter_content(chunk):
                block = np.frombuffer(block, dtype=np.int16())
                plt.clf()
                plt.plot(fft(block))
                plt.pause(0.001)
        except KeyboardInterrupt:
            break


def mbari_spec(n=128, chunk=1024, fs=44100):
    stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'
    r = requests.get(stream_url, stream=True)

    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    def get_spectrum(block):
        block = np.frombuffer(block, dtype=np.int16())
        f, _, Sxx = signal.spectrogram(block, fs=fs, nfft=chunk)
        return f, np.log10(Sxx)
    
    block = r.raw.read(chunk)
    #block = np.reshape(block, (block.shape[0], 1))
    _, Sxx = get_spectrum(block)
    h, w = Sxx.shape
    sxx = np.zeros((h, w*n))
    t = [*range(w*n)]

    while True:
        try:
            for block in r.iter_content(chunk):
                f, Sxx = get_spectrum(block)
                Sxx = minmax_scale(Sxx, (0, 1))
                sxx[:, :w] = Sxx
                sxx = minmax_scale(sxx, (0, 1))
                plt.clf()
                plt.pcolormesh(t, f, sxx, cmap='jet')
                plt.pause(0.001)
                sxx = np.roll(sxx, w, axis=1)
        except KeyboardInterrupt:
            break


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

    def get_spectrum(stream, chunk):
        data = stream.read(chunk, exception_on_overflow=False)
        data = np.frombuffer(data, dtype=np.int16())
        f, _, Sxx = signal.spectrogram(data, fs=fs, nfft=1024)
        return f, 10*np.log10(Sxx)

    _, Sxx = get_spectrum(stream, chunk)
    h, w = Sxx.shape
    sxx = np.zeros((h, w*n))
    t = [*range(w*n)]

    while True:
        try:
            f, Sxx = get_spectrum(stream, chunk)
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


def plot_spectrogram(filename, max_freq=24000):
    fs, x = wavfile.read(filename)
    f, t, sxx = signal.spectrogram(x[:,0], fs, nfft=1024)  # channel 0

    # cut to maximum frequency
    f = f[f < max_freq]
    sxx = np.log10(sxx[:f.size])
    
    # normalize
    sxx = (sxx - np.min(sxx)) / (np.max(sxx) - np.min(sxx))

    plt.pcolormesh(t, f, sxx, cmap='jet')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')

    plt.show()
    
    return t, f, sxx


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




