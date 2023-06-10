# records mbbari stream to .wav file and plays the file

import utils
import argparse

description = """Records a stream from MBARI hydrophone to file.\n"""
parser = argparse.ArgumentParser(description)
parser.add_argument('-f', '--filename', type=str, help='ouput filename',
                    default='stream.mp3')
parser.add_argument('-d', '--duration', type=float,
                    help='recording duration in seconds', default=5.0)

args = parser.parse_args()
wav_fname = args.filename[:-4] + '.wav'

utils.mbari_stream(args.filename, args.duration)
utils.mp3_to_wav(args.filename, wav_fname)
print("playing: ", wav_fname)
utils.play_wav(wav_fname)
