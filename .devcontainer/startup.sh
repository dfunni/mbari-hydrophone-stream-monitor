#!/bin/sh
sudo apt-get update && sudo apt-get install ffmpeg libsm6 libxext6 ssh-askpass -y
python3 -m pip install --user -r requirements.txt

echo "alias ll='ls -lh'" > ~/.bash_aliases
cp /workspaces/mbari-hydrophone-stream-monitor/.devcontainer/.bash_profile ~
source ~/.bash_profile