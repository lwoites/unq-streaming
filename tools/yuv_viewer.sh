#!/bin/bash

color_format=$1
width=$2
height=$3
file=$4

gst-launch-1.0 filesrc location=$file ! rawvideoparse format=y$color_format width=$width height=$height framerate=1/1 ! imagefreeze ! videoconvert ! autovideosink
