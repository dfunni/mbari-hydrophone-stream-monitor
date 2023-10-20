import warnings
warnings.filterwarnings("ignore")

import torch
import yaml
from argparse import ArgumentParser
from torch import multiprocessing
import torchaudio.transforms as T

from pipeline import preproccess, BinaryClassifier


def main(filename, transform, net):
    with torch.no_grad():
        X = preproccess(filename, transform).unsqueeze(0)
        # calculate outputs by running images through the network
        output = net(X)
        return output.round().int().item()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    torch.set_default_tensor_type('torch.FloatTensor')
    multiprocessing.set_start_method('spawn')

    with open('infer_config.yaml', 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.Loader)

    net = BinaryClassifier()
    net.load_state_dict(torch.load(config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth',
                                   map_location=torch.device('cpu')))

    transform = T.MelSpectrogram(**config['torch_melspec_params']).cpu()
  
    output = main(args.filename, transform, net)
    print(output)