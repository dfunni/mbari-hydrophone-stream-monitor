# MBARI Hydrophone Stream Monitor

Ultimately, this project will monitor the MBARI hydrophone stream at https://www.mbari.org/soundscape-listening-room/ and send out alerts when humpback whales are vocalizing.

### data-collection 
shell scripts to collect 10 sec data snippets to build dataset, these are run at regular intervals on a rasberry pi
### MARS-data-tagger
dash webapp with the following functionality:
- data pulls from raspberry pi data collector
- spectrogram visualization and audio control
- clip labeling
- dataset statistics visualization

![](screenshots/MARS-data-tagger.png)

References:
J. Ryan et al., "New Passive Acoustic Monitoring in Monterey Bay National Marine Sanctuary," OCEANS 2016 MTS/IEEE Monterey, Monterey, CA, USA, 2016, pp. 1-8, doi: 10.1109/OCEANS.2016.7761363.
