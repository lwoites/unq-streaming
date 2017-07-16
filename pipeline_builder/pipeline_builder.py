#!/usr/bin/env python
# - coding: UTF-8 -

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst

import pipelines


class Application(object):

    @staticmethod
    def registered_pipelines():
        pipes = []
        for symbol in dir(pipelines):
            symbol_l = symbol.lower()
            if (symbol_l.endswith("pipeline") or symbol_l.startswith("pipeline")) and symbol_l != "basepipeline":
                pipes.append(symbol)
        return pipes

    def __init__(self):
        self.main_loop = None
        self.pipeline = None

    def initialize(self):
        GObject.threads_init()
        Gst.init(None)

    def bus_call(self, bus, message, loop):
        msg_type = message.type
        if msg_type == Gst.MessageType.EOS:
            print "End-of-stream message received"
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
            loop.quit()
        elif msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print "Error: %s: %s\n" % (err, debug)
            self.pipeline = None
            loop.quit()
        return True

    def clock_cb(self, clock, time_, id_, finish_time):
        if self.pipeline.current_state == Gst.State.PLAYING:
            running_time = time_ - self.pipeline.get_base_time()
            print "Runnig Time:", (running_time / Gst.SECOND), "| finish_time:", finish_time / Gst.SECOND
            if running_time > 0 and running_time >= finish_time:
                print "Stopping the pipeline"
                self.pipeline.send_event(Gst.Event.new_eos())

    def run(self, args):
        self.initialize()
        try:
            self.pipeline, finish_time = self._build_pipeline(args)
        except Exception as error:
            self._error_and_exit("Error al constuir el pipeline ¿Pasaste bien los parametros?", error)
        self.main_loop = self._build_loop(self.pipeline.get_bus())
        self._run(finish_time)

    def clean(self):
        if self.pipeline != None:
            self.pipeline.send_event(Gst.Event.new_eos())
            self.pipeline.get_bus().timed_pop_filtered(
                Gst.CLOCK_TIME_NONE,
                Gst.MessageType.EOS | Gst.MessageType.ERROR
            )
            self.pipeline.set_state(Gst.State.NULL)

    def _build_loop(self, message_bus):
        # create and event loop and feed gstreamer bus mesages to it
        loop = GObject.MainLoop()
        message_bus.add_signal_watch()
        message_bus.connect("message", self.bus_call, loop)
        return loop

    def _register_cb(self, finish_time):
        if finish_time > 0:
            self.periodic_id = self.pipeline.get_pipeline_clock().new_periodic_id(
                0, Gst.SECOND
            )
            self.pipeline.get_pipeline_clock().id_wait_async(
                self.periodic_id, self.clock_cb, finish_time * Gst.SECOND
            )

    def _run(self, finish_time):
        # start play back and listen to events
        self.pipeline.set_state(Gst.State.PLAYING)
        self._register_cb(finish_time)
        try:
            self.main_loop.run()
        except:
            pass
        self.clean()

    def _get_pipeline_builder(self, pipeline_name):
        if hasattr(pipelines, pipeline_name):
            return getattr(pipelines, pipeline_name)()
        else:
            self._error_and_exit("Pipeline {} no esta definido en pipelines.py".format(pipeline_name))

    def _build_pipeline(self, args):
        pipeline_builder = self._get_pipeline_builder(args[1])
        return pipeline_builder.build_pipeline(args[2:]), pipeline_builder.finish_time()

    def _error_and_exit(self, message, exception=None):
        print message
        print "-" * 80
        if exception is not None:
            raise
        sys.exit(1)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print Application.registered_pipelines()
    else:
        sys.exit(Application().run(sys.argv))
