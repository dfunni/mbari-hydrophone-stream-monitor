import utils
import argparse



description = """Converts a mp3 file to wav."""
parser = argparse.ArgumentParser(description)
parser.add_argument('-f', '--filename', type=str, help='ouput filename',
                    default='stream.mp3')
parser.add_argument('-d', '--directory', type=str,
                    default='./')

args = parser.parse_args()

tmp = args.directory + args.filename
out = args.directory + args.filename[:-4] + '.wav'

utils.mp3_to_wav(tmp, out)