#!/bin/bash

rm hls/*
cp playlist.m3u8 hls/
cd hls 
python2 ../../pipeline_builder/pipeline_builder.py AdaptativeStreamingPipeline &
cd ..
python2 -m SimpleHTTPServer 8000 .
