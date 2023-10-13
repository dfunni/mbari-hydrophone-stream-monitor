import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import pandas as pd
import torch
import yaml
from tqdm import tqdm

import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch import multiprocessing

from mars_model import SimpleCNN
from mars_dataset import MARSDataset


def get_data():
    data = pd.read_json(config['DATASET_ROOT'] + config['DATASET_JSON'])
    data.dropna(inplace=True)
    data['y'] = data['label'].apply(lambda x: 1 if x != 'no_whale' else 0) # baseline
    # data['y'] = data['label'].apply(lambda x: 1 if x == 'whale+' else 0) # highSNR

    X_train, X_val = train_test_split(data, 
                                    test_size=config['TEST_SIZE'], 
                                    random_state=config['RANDOM_STATE'],
                                    stratify=data['y'],
                                    )

    trainset = MARSDataset(X_train)
    valset = MARSDataset(X_val)

    train_loader = DataLoader(trainset,
                            batch_size=config['N_BATCH'], 
                            shuffle=True, 
                            num_workers=2,
                            generator=torch.Generator(device='cuda'))

    val_loader = DataLoader(valset, 
                            batch_size=config['N_BATCH'], 
                            shuffle=True, 
                            num_workers=2,
                            generator=torch.Generator(device='cuda'))


    return train_loader, val_loader

def train(train_loader, criterion, optimizer, save=False):
    ## Train the baseline model
    for epoch in range(config['N_EPOCHS']):
        print(f'Epoch: {epoch+1} / {config["N_EPOCHS"]}')
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(tqdm(train_loader), 0):
            
            # move data to GPU
            inputs = inputs.unsqueeze(1).to(torch.device('cuda'))        
            labels = labels.to(torch.device('cuda'))
            
            # check that inputs are valid
            assert ~torch.isnan(inputs).any(), f'input error (nan): {inputs}'
            assert ~torch.isinf(inputs).any(), f'input error (inf): {inputs}'
            
            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = net(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # generate statistics
            running_loss += loss.item()

        print(f'Loss: {running_loss / (i+1)}')

    print('Finished Training')
    if save:
        torch.save(net.state_dict(), config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth')


def load_model():
    ## Load saved model
    net.load_state_dict(torch.load(config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth'))


def validate(val_loader):
    ## Validate with hold out validation set
    y_true = []
    y_pred = []

    # since we're not training, we don't need to calculate the gradients for our outputs
    with torch.no_grad():
        for i, (inputs, labels) in enumerate(tqdm(val_loader)):
            inputs = inputs.unsqueeze(1).to(torch.device('cuda'))
            labels = labels.to(torch.device('cuda'))
            # calculate outputs by running images through the network
            outputs = net(inputs)
            # the class with the highest energy is what we choose as prediction
            _, predicted = torch.max(outputs.data, 1)
            y_true += labels.cpu().tolist()
            y_pred += predicted.cpu().tolist()

    # print(f'Accuracy of the network on the testset: {(correct / total):.4f}')
    print(f'Accuracy:  {accuracy_score(y_true, y_pred):.4f}')
    print(f'Precision: {precision_score(y_true, y_pred):.4f}')
    print(f'Recall:    {recall_score(y_true, y_pred):.4f}')
    print(f'F1:        {f1_score(y_true, y_pred):.4f}')


if __name__ == '__main__':
    torch.cuda.empty_cache()
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    multiprocessing.set_start_method('spawn')

    with open('detector_config.yaml', 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.Loader)

    train_loader, val_loader = get_data()
    
    net = SimpleCNN()
    net.cuda()
    
    if config['TRAIN']:
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
        train(train_loader, criterion, optimizer, save=config['SAVE'])
    else:
        load_model()
    
    validate(val_loader)

