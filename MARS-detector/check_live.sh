#!/bin/bash
mm=0
ss=10
tmp_file=tmp.mp3
save_file=whales/$(date --utc +%Y%m%d_%H%M%SZ).mp3

usage() {
    echo "Usage: $0 [ -m minutes ] [ -s seconds ] [-o output ]" 1>&2
}
exit_abnormal() {
    usage
    exit 1
}

while getopts "hm:s:o:" flag; do
    case "${flag}" in
        m) 
            mm=${OPTARG}
            re_isanum='^[0-9]+$'                    # Regex: match whole numbers only
            if ! [[ $TIMES =~ $re_isanum ]] ; then  # if $TIMES not whole:
                echo "Error: TIMES must be a positive, whole number."
                exit_abnormal
            fi
            ;;
        s) 
            ss=${OPTARG}
            re_isanum='^[0-9]+$'                    # Regex: match whole numbers only
            if [[ $TIMES =~ $re_isanum ]] ; then    # if $TIMES not whole:
                echo "Error: TIMES must be a positive, whole number."
                exit_abnormal
            elif [ $TIMES -eq "0" ]; then           # If it's zero:
                echo "Error: TIMES must be greater than zero."
                exit_abnormal                       # Exit abnormally.
            fi
            ;;
        o)
            output=${OPTARG}
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
python infer.py $tmp_file 1>&1
if [[ $? = 1 ]] ; then
    echo WHALE!;
    cp $tmp_file $save_file
else
    echo "NO WHALE";
fi
rm $tmp_file
