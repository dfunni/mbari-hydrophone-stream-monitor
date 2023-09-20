#!/bin/bash

samples=6

usage() {
    echo "Usage: $0 [ -s smaples ]" 1>&2
}
exit_abnormal() {
    usage
    exit 1
}

while getopts "hs:" flag; do
    case "${flag}" in
        s) 
            samples=${OPTARG}
            re_isanum='^[0-9]+$'                    # Regex: match whole numbers only
            if [[ $TIMES =~ $re_isanum ]] ; then    # if $TIMES not whole:
                echo "Error: TIMES must be a positive, whole number."
                exit_abnormal
            elif [ $TIMES -eq "0" ]; then           # If it's zero:
                echo "Error: TIMES must be greater than zero."
                exit_abnormal                       # Exit abnormally.
            fi
            ;;      
        h) 
            exit_abnormal
            ;;
        *)                                          # If unknown (any other) option:
            exit_abnormal                           # Exit abnormally.
            ;;
    esac
done

for ((i=1; i<=samples; i++))
do
    ./mbari_record.sh
    sleep 7
done

