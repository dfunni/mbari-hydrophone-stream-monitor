import warnings
warnings.filterwarnings("ignore")

import torch
import torchaudio



def preproccess(filename, transform):
    '''Performs transform to turn audio into spectrum/ceptstrum tensor
    Args: 
        filename [str]: audio file name
        transform: torch.transfrorms object
    Returns:
        X [tensor]: spectrogram tensor'''
    samples, _ = torchaudio.load(filename)
    samples = samples[::2].cpu()
    X = transform(samples)[:,:180,5:]
    # logarithmic transformation mapping to [1..100]
    X = 99*(X - X.min()) / (X.max() - X.min()) + 1
    X = torch.log10(X)
    X = (X - X.min()) / (X.max() - X.min()) # map to [0..1]
    return X


def mfcc_transform(filename, transform):
    samples, _ = torchaudio.load(filename)
    samples = samples[::2].cuda()
    X = transform(samples)[:,:180,5:]
    X = (X - X.min()) / (X.max() - X.min()) # map to [0..1]
    return X
