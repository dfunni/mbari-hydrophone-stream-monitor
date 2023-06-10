import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = int(44.1e3)
CHUNK = int(1024)
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = 'file.wav'

audio = pyaudio.PyAudio()

# start recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("recording...")
frames = []

for i in range(int(RATE/CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

print("finished recording")

# stop recording
stream.stop_stream()
stream.close()
audio.terminate()

wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)
wave_file.writeframes(b''.join(frames))
wave_file.close()
