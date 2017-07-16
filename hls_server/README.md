# Simple Hls Server

A Live Hls Server implemented using pipeline_builder and python2 SimpleHTTPServer.
It gets the video from your webcam.

## Running

```
cd hls_server
./run.sh
```
This will encode in two qualities and the generated segments will be in the hls dir.

## Seeing the stream

Enter to http://0.0.0.0:8000/player.html and enjoy