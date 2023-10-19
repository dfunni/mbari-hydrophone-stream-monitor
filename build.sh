#!/bin/bash
cd /home/dfunni/mbari-hydrophone-stream-monitor/ 
docker build --network=host -t mars-detect .
