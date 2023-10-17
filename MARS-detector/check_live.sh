#!/bin/bash
mm=0
ss=10
tmp_file=tmp.mp3
save_file=whales/$(date --utc +%Y%m%d_%H%M%SZ).mp3
outcode=0

usage() {
    echo "Usage: $0 [ -m minutes ] [ -s seconds ] [-o output ]" 1>&2
}
exit_abnormal() {
    usage
    exit 1
}

while getopts "h:o:" flag; do
    case "${flag}" in
        o)
            save_file=${OPTARG}
            ;;
        h) 
            exit_abnormal
            ;;
        :)                                          # If expected argument omitted:
            echo "Error: -${OPTARG} requires an argument."
            exit_abnormal                           # Exit abnormally.
            ;;
        *)                                          # If unknown (any other) option:
            exit_abnormal                           # Exit abnormally.
            ;;
    esac
done

ffmpeg -y -t 00:$mm:$ss -i https://shoutcast.mbari.org/pacific-soundscape $tmp_file
ret=$(python infer.py $tmp_file)
if [[ $ret = 1 ]] ; then
    echo WHALE!;
    cp $tmp_file $save_file
else
    echo "no whale :(";
fi
rm $tmp_file
