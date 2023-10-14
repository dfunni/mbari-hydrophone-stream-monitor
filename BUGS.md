## Bugs
1) Occasionally MARS data tagger the page hangs after button press
    + implemented refresh plot button to manage

2) Models trained on high SNR whale vocalizations biased toward no_whale classification due to unbalanced data
    + Implement undersampling and re-train

3) Some spectrograms blown out

TODO: 
- investigate normalization issues to resolve blown out spectrograms
- Implement k-fold cross-validation
- Implement cepstrum analysis