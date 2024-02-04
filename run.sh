#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker container prune -f
docker run  \
    --name mars-detect \
    --network host \
    --mount type=bind,source="$(pwd)",target=/workspaces/mbari-hydrophone-stream-monitor \
    --mount type=bind,source="/home/dfunni/data",target=/data \
    --mount type=bind,source="/var/log",target=/var/log \
    mars-detect /workspaces/mbari-hydrophone-stream-monitor/start.sh
