from torch.utils.data import Dataset
import torch
import os


class MARSDataset(Dataset):
    def __init__(self, dataframe):
        self.filename = dataframe["filename"]
        self.label = dataframe["y"]

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        fname = self.filename.iloc[idx]
        y = self.label.iloc[idx]
        basename = os.path.splitext(fname)[0]
        datapath = os.path.join('./data/', basename + '.pt')
        X = torch.load(datapath)
        return X, y, fname
