import requests

stream_url = 'http://streamingv2.shoutcast.com/ocean-soundscape?lang=en-us'

r = requests.get(stream_url, stream=True)

with open('whalesx.mp3', 'wb') as f:

    for block in r.iter_content(1024):
        try:
            f.write(block)
        except KeyboardInterrupt:
            break
