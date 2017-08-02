#!/bin/bash

YUV_FILE="$1"
WIDTH=$2
HEIGHT=$3
DEST_FILE="$4"

gst-launch-1.0 filesrc location=$YUV_FILE ! rawvideoparse width=$WIDTH height=$HEIGHT format="y444" framerate=1/1 ! videoconvert ! pngenc !  filesink location=$DEST_FILE
