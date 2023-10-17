#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker build --network=host -t mars-detect .
docker run  -it -d \
    --name mars-detect \
    --network host \
    --mount type=bind,source="$(pwd)",target=/app \
    --mount type=bind,source="/home/dfunni/data",target=/app/data \
    mars-detect ./start.sh
