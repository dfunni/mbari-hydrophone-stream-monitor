FROM "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye"
WORKDIR /app
RUN apt-get update
RUN apt-get install -y ffmpeg libsm6 libxext6 ssh-askpass
COPY requirements.txt ./
RUN pip install -r requirements.txt
ENTRYPOINT ["/bin/sh"]
