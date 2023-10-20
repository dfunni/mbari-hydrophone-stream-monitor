import warnings
warnings.filterwarnings("ignore")

from argparse import ArgumentParser
import yaml
import logging

import torch
from torch import multiprocessing
import torchaudio.transforms as T

from pipeline import preproccess, BinaryClassifier


def main(filename, transform, net):
    with torch.no_grad():
        X = preproccess(filename, transform).unsqueeze(0)
        # calculate outputs by running images through the network
        try:
            output = net(X)
        except:
            logging.error('inference error')
        logging.debug(f'Inference output for {filename}: {output.item():.4f}')
        return output.round().int().item()


if __name__ == "__main__":
    
    torch.set_default_tensor_type('torch.FloatTensor')
    multiprocessing.set_start_method('spawn')

    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    with open('infer_config.yaml', 'r') as ymlfile:
        config = yaml.safe_load(ymlfile.read())

    logging.basicConfig(format='%(asctime)s-%(process)d-%(levelname)s-%(message)s',
                        datefmt='%d-%b-%y %H:%M:%S', 
                        level="DEBUG",
                        filename='/workspaces/mbari-hydrophone-stream-monitor/MARS-detector/infer.log',
                        filemode='a')

    net = BinaryClassifier()
    net.load_state_dict(torch.load(config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth',
                                   map_location=torch.device('cpu')))

    transform = T.MelSpectrogram(**config['melspec_params']).cpu()
  
    output = main(args.filename, transform, net)
    
    print(output)