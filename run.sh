#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker build --network=host -t MARS-detect .
docker run --network host --mount type=bind,source="$(pwd)",target=/app MARS-detect
