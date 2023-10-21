"""This script is a python wrapper for rsync command to pull data from raspi server."""
import os

def pull_data(tmp_location='assets/data/new_data/', save_location='assets/data/'):
    os.system(f'rsync -avz --remove-source-files -e "ssh -i /home/vscode/.ssh/id_rsa" dfunni@192.168.0.141:/home/dfunni/data/* {tmp_location}')
    new_files = os.listdir(tmp_location)
    os.system(f'mv {tmp_location}* {save_location}')
    return new_files
