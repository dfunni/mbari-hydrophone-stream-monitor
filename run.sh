#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker container prune -f
docker run  \
    --name mars-detect \
    --network host \
    --mount type=bind,source="$(pwd)",target=/app \
    --mount type=bind,source="/home/dfunni/data",target=/app/data \
    mars-detect ./start.sh
