#!/bin/bash

PNG_FILE="$1"
DEST_FILE="$2"

if [ -s $PNG_FILE ]; then
	echo "El archivo $PNG_FILE no existe"
    exit 1
fi

GST_DEBUG=0 gst-launch-1.0 filesrc location=$PNG_FILE  ! pngdec ! videoconvert   !  video/x-raw, format="Y444" !  filesink location=$DEST_FILE
