import warnings
warnings.filterwarnings("ignore")

import os
import matplotlib.pyplot as plt
import pandas as pd
import torch
import yaml

from torch import multiprocessing
import torchaudio
import torchaudio.transforms as T

torch.cuda.empty_cache()
torch.set_default_tensor_type('torch.cuda.FloatTensor')
multiprocessing.set_start_method('spawn')

with open('detector_config.yaml', 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.Loader)

data = pd.read_json(config['DATASET_ROOT'] + config['DATASET_JSON'])
data.dropna(inplace=True) # drop unlabeled files
data['y'] = data['label'].apply(lambda x: 1 if x == 'whale+' else 0)

def spec_transform(filename, transform):
    samples, _ = torchaudio.load(os.path.join(config['DATA_ROOT'], filename))
    samples = samples[::2].cuda()
    sxx = transform(samples)[:,:180,5:]
    # logarithmic transformation mapping to [1..100]
    sxx = 99*(sxx - sxx.min()) / (sxx.max() - sxx.min()) + 1
    sxx = torch.log10(sxx)
    sxx = (sxx - sxx.min()) / (sxx.max() - sxx.min()) # map to [0..1]
    torch.save(sxx.cpu(), os.path.join('./data/', os.path.splitext(filename)[0] + '.pt'))

def mfcc_transform(filename, transform):
    samples, _ = torchaudio.load(os.path.join(config['DATA_ROOT'], filename))
    samples = samples[::2].cuda()
    sxx = transform(samples)[:,:180,5:]
    sxx = (sxx - sxx.min()) / (sxx.max() - sxx.min()) # map to [0..1]
    torch.save(sxx.cpu(), os.path.join('./data/', os.path.splitext(filename)[0] + '.pt'))

if __name__ == "__main__":

    if config['TRANSFORM'] == 'spectrogram':
        transform = T.Spectrogram(**config['torch_spectrogram_params']).cuda()
        _ = data['filename'].apply(lambda x: spec_transform(x, transform))

    elif config['TRANSFORM'] == 'melspectrogram':
        transform = T.MelSpectrogram(**config['torch_melspec_params']).cuda()
        _ = data['filename'].apply(lambda x: spec_transform(x, transform))
    
    elif config['TRANSFORM'] == 'mfcc':
        transform = T.MFCC(n_mfcc=180, melkwargs=config['torch_melspec_params']).cuda()
        _ = data['filename'].apply(lambda x: mfcc_transform(x, transform))




