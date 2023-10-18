import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
import pandas as pd
import torch
import yaml
from tqdm import tqdm

import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch import multiprocessing


from mars_model import BinaryClassifier
from mars_dataset import MARSDataset

with open('detector_config.yaml', 'r') as ymlfile:
    config = yaml.load(ymlfile, Loader=yaml.Loader)


def train(loader):   
    running_loss = 0.0
    for i, (inputs, labels, _) in enumerate(tqdm(loader), 0): # loop through batches
        # move data to GPU
        inputs = inputs.cuda()  
        labels = labels.cuda().float()
        
        # check that inputs are valid
        assert ~torch.isnan(inputs).any(), f'input error (nan): {inputs}'
        assert ~torch.isinf(inputs).any(), f'input error (inf): {inputs}'
        
        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs).squeeze()
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # generate statistics
        running_loss += loss.item()
    train_loss = running_loss / (i+1)
    return train_loss


def validate(loader):
    running_vloss = 0.0
    y_true = []
    y_pred = []
    with torch.no_grad():
        for i, (vinputs, vlabels, _) in enumerate(tqdm(loader)):
            vinputs = vinputs.cuda()
            vlabels = vlabels.cuda().float()
            # calculate outputs by running images through the network
            voutputs = net(vinputs).squeeze()
            vloss = criterion(voutputs, vlabels)
            running_vloss += vloss
            predicted = voutputs.round() # for binary classifier with sigmoid
            y_true += vlabels.cpu().tolist()
            y_pred += predicted.cpu().tolist()
    val_loss = running_vloss / (i+1)
    return val_loss, (y_true, y_pred)
    


if __name__ == "__main__":
    torch.cuda.empty_cache()
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
    multiprocessing.set_start_method('spawn')

    data = pd.read_json(config['DATASET_ROOT'] + config['DATASET_JSON'])
    data.dropna(inplace=True)
    data['y'] = data['label'].apply(lambda x: 1 if x == 'whale+' else 0)

    # balance dataset since there are many fewer whale samples than no_whale
    num_whale = data[data['y'] == 1]['y'].count() 
    whale = data[data['y'] == 1]
    nowhale = data[data['y'] == 0].sample(n=num_whale, random_state=1)
    data = pd.concat([whale, nowhale])

    X_train, X_val = train_test_split(data, 
                                      test_size=config['TEST_SIZE'], 
                                      random_state=config['RANDOM_STATE'],
                                      stratify=data['y'])
    trainset = MARSDataset(X_train)
    testset = MARSDataset(X_val)


    trainloader = DataLoader(trainset,
                            batch_size=config['N_BATCH'], 
                            shuffle=True, 
                            num_workers=2,
                            generator=torch.Generator(device='cuda'))

    testloader = DataLoader(testset, 
                            batch_size=config['N_BATCH'], 
                            shuffle=True, 
                            num_workers=2,
                            generator=torch.Generator(device='cuda'))

    net = BinaryClassifier().cuda()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(net.parameters(),
                        lr=config['LEARNING_RATE'])
    
    min_loss = 1000000.0

    for epoch in range(config['N_EPOCHS']): # loop through epochs
        print(f'Epoch: {epoch+1} / {config["N_EPOCHS"]}')
        net.train()
        train_loss = train(trainloader)
        net.eval()
        val_loss, _ = validate(testloader)

        print(f'LOSS train {train_loss:.4f} | val {val_loss:.4f}')

        # save off model if best performing yet
        if val_loss < min_loss:
            min_loss = val_loss
            print('saving...')
            torch.save(net.state_dict(), config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth')
    
    # finally load best performing net and get performance metrics
    net = BinaryClassifier().cuda()
    net.load_state_dict(torch.load(config['MODEL_ROOT'] + config['MODEL_NAME'] + '.pth'))
    val_loss, (y_true, y_pred) = validate(testloader)
    try:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    except:
        pass

    # print(f'Accuracy of the network on the testset: {(correct / total):.4f}')
    print(f'Accuracy:  {accuracy_score(y_true, y_pred):.4f}')
    print(f'Precision: {precision_score(y_true, y_pred):.4f}')
    print(f'Recall:    {recall_score(y_true, y_pred):.4f}')
    print(f'F1:        {f1_score(y_true, y_pred):.4f}')
    print(f'Confusion:\n\tTP: {tp}\n\tFP: {fp}\n\tTN: {tn}\n\tFN: {fn}')
