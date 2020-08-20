import utils
import os

#filename = 'whales'
#tmp = filename + '.mp3'
#out = filename + '.wav'
#utils.mic_record(out, time_s=5, rate=44100)
#utils.mbari_stream(tmp, duration_s=5)
#utils.mp3_to_wav(tmp, out)
#print("playing: ", out)
#utils.play_wav(out)

#_ = utils.plot_spectrogram(out)
utils.stream_spec(chunk=1024, fs=48000)