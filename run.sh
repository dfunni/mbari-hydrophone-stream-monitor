#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker container prune -f
docker run  \
    --name mars-detect \
    --network host \
    --mount type=bind,source="$(pwd)",target=/workspaces/mbari-hydrophone-stream-monitor \
    --mount type=bind,source="/home/dfunni/data",target=/data \
    mars-detect /workspaces/mbari-hydrophone-stream-monitor/start.sh
