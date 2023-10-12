from torch.utils.data import Dataset
# from torch import set_default_tensor_type, isnan
from mars_clip import MarsClip
# from torch import from_numpy
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# set_default_tensor_type('torch.cuda.FloatTensor')

class MARSDataset(Dataset):
    def __init__(self, dataframe):
        self.filename = dataframe["filename"]
        self.label = dataframe["y"]

    def __len__(self):
        return len(self.label)

    def __getitem__(self, idx):
        fname = self.filename.iloc[idx]
        clip = MarsClip(fname)
        sxx, _, _ = clip.get_spec_img()
        sxx = np.nan_to_num(sxx)
        
        sxx = (sxx - sxx.min()) / (sxx.max() - sxx.min())
        # sxx = from_numpy(sxx,)
        # sxx = sxx[None,:,:]
        label = self.label.iloc[idx]
        return sxx, label