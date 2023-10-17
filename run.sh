#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker build --network=host -t mars-detect .
docker run --name mars-detect -itd --network host --mount type=bind,source="$(pwd)",target=/app mars-detect
