"""This script is a python wrapper for rsync command to pull data from raspi server.
"""

import os

def pull_data():
    os.system('rsync -avz --remove-source-files -e "ssh -i /home/vscode/.ssh/id_rsa" dfunni@192.168.0.141:/home/dfunni/data/* /data/new_data/')