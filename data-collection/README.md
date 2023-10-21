This code uses ffmpeg to collect 10s segments of audio from the stream found at https://www.mbari.org/project/soundscape-listening-room/.

mbari_record.sh - collects a single 10s segment
    usage: mbari_collect.sh [ -m minutes ] [ -s seconds ] [ -o output ]

data_collect.sh - runs mbari_record.sh multiple times to collect a series of audio samples
    usage: data_collect.sh [ -s smaples ]