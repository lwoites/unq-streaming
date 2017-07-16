# Pipeline Builder

Tool made for early CS students that:
1. Not necessaraly knows python
2. Doesn't know gstreamer

 The idea is that the students apply the concepts of
 video processing by building a pipeline and ignoring the
 initialization and running code of gstreamer.

 ## Running

`python pipeline_builder.py` will lists all the pipelines defined
in pipelines.py

To run a specific pipeline.
`python pipeline_builder.py <PIPELINE_NAME> [PIPE_ARG1] [PIPE_ARG2]`

## Defining new pipelines

To define a new pipeline you have to:
1. Define a new class on the `pipelines.py` file and MUST have de word Pipeline
at the beginning or the end of the class name.
2. Define the method `build_pipeline(self, args)` that have to return a `Gst.Pipeline`
3. You are encouraged to subclass from `BasePipeline` to reuse some of the methods defined there.

## Dependendies

* Python2
* gst-Python
* gstreamer and as much plugins as you need :)