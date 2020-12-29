import utils
import argparse


description = """Plots wav file."""
parser = argparse.ArgumentParser(description)
parser.add_argument('-f', '--filename', type=str, help='filename',
                    default='stream.wav')
parser.add_argument('-d', '--directory', type=str, help='directory',
                    default='/Users/dave/data/MBARI_hydrophone_data/')

args = parser.parse_args()

if args.filename[-4:] == '.wav':
    out = args.directory + args.filename
else:
    out = args.directory + args.filename + '.wav'


_ = utils.plot_spectrogram(out)