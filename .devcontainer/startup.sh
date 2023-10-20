#!/bin/sh
pip install dash-mantine-components # for some reason this did not work in requirements.txt

echo "alias ll='ls -lh'" > ~/.bash_aliases
cp /workspaces/mbari-hydrophone-stream-monitor/.devcontainer/.bash_profile ~
source ~/.bash_profile