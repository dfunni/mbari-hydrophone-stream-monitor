FROM "mcr.microsoft.com/devcontainers/python:13.11-bullseye"
WORKDIR /app
RUN apt-get update
RUN apt-get install -y ffmpeg libsm6 libxext6 ssh-askpass
COPY requirements.txt ./
RUN pip install -r requirements.txt
# COPY start.sh mailpass.env MARS-detector/models/net.pth MARS-detector/infer* MARS-detector/check_live.sh MARS-detector/mars_model.py /app/
CMD ["/bin/sh"]
