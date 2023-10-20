FROM "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye"
WORKDIR /workspaces/mbari-hydrophone-stream-monitor
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 ssh-askpass
COPY requirements.txt ./
RUN pip install -r requirements.txt
ENTRYPOINT ["/bin/sh"]
