# script to move models to raspberry pi for production

#!/bin/bash


usage() {
    echo "Usage: $0  <model.pth>" 1>&2
}
exit_abnormal() {
    usage
    exit 1
}

if [[ $# -ne 1 ]]; then
    exit_abnormal
fi

while getopts "h:" flag; do
    case "${flag}" in
        h)
            exit_abnormal
            ;;
        *)
            exit_abnormal
            ;;
    esac
done

scp /workspaces/mbari-hydrophone-stream-monitor/MARS-detector/models/$1 dfunni@192.168.0.141:/home/dfunni/mbari-hydrophone-stream-monitor/MARS-detector/models/net.pth
