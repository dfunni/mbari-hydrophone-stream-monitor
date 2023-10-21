This module contains code to preprocess data, train machine learning models, and run inference on data files.

Configuration for training is set in the detector_config.yaml and for inference configuration is done in infer_config.yaml

Experimentation is done in the Jupyter notebooks and codified in the .py files.

scp_model.sh is used to copy files from the trianing machine to the Raspberry Pi for inference.

check_live.sh is the primary inference script that collects a sample of data, runs inference, and performs follow on actions.