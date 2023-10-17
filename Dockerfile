FROM "mcr.microsoft.com/devcontainers/python:1-3.11-bullseye"
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY run.py start.sh mailpass.env MARS-detector/models/net.pth MARS-detector/infer.py /app/
CMD ["/bin/sh", "/app/start.sh"]
