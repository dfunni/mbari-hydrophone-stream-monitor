#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker build --network=host -t mars-detect .
docker run  -d \
    -t \
    --name mars-detect \
    --network host \
    --mount type=bind,source="$(pwd)",target=/app \
    --mount type=bind,source="/home/dfunni/data",target=/app/MARS-detector/whales \
    mars-detect
