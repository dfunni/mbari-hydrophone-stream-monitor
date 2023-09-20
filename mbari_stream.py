'''
This script tests methods to record for accurate durations
'''

import requests
import argparse
import time

config_file = "config.yaml"

with open(config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

def stream_record(filename, duration):

    stream_url = config['stream_url']

    r = requests.get(stream_url, stream=True)
    print(f'Redording for {duration}s.\nPress ctrl-C to stop recording.')

    with open(filename, 'wb') as f:
        t0 = time.time()
        for block in r.iter_content(1024):
            if (time.time() - t0) < duration:
                try:
                    f.write(block)

                except KeyboardInterrupt:
                    break
            else:
                break


if __name__ == "__main__":

    description = """Records a stream from MBARI hydrophone to file.\n"""
    parser = argparse.ArgumentParser(description)
    parser.add_argument('-f', '--filename', type=str, help='ouput filename',
                        default='stream.mp3')
    parser.add_argument('-d', '--duration', type=float,
                        help='recording duration in seconds', default=10.0)
    args = parser.parse_args()

    stream_record(args.filename, args.duration)
