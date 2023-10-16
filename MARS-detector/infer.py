import warnings
warnings.filterwarnings("ignore")

import numpy as np
import torch
import yaml
import os
from argparse import ArgumentParser
from torch import multiprocessing
import torchaudio
import torchaudio.transforms as T

from mars_model import BinaryClassifier

def preproccess(filename, transform):
    '''Performs transform to turn audio into spectrum/ceptstrum tensor
    Args: 
        filename [str]: audio file name
        transform: torch.transfrorms object
    Returns:
        X [tensor]: spectrogram tensor'''
    samples, _ = torchaudio.load(os.path.join(filename))
    samples = samples[::2].cuda()
    X = transform(samples)[:,:180,5:]
    # logarithmic transformation mapping to [1..100]
    X = 99*(X - X.min()) / (X.max() - X.min()) + 1
    X = torch.log10(X)
    X = (X - X.min()) / (X.max() - X.min()) # map to [0..1]
    return X


def main(filename, transform, net):
    with torch.no_grad():
        X = preproccess(filename, transform).unsqueeze(0)
        # calculate outputs by running images through the network
        output = net(X)
        if output.round().item():
            call = 'whale'
        else:
            call = 'no whale'
        return output.round().int().item()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    torch.cuda.empty_cache()
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    multiprocessing.set_start_method('spawn')

    with open('infer_config.yaml', 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.Loader)

    net = BinaryClassifier().cuda()
    net.load_state_dict(torch.load(config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth'))

    transform = T.MelSpectrogram(n_mels=180, **config['torch_melspec_params']).cuda()
  
    output = main(args.filename, transform, net)
    print(output)