
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject
from gi.repository import Gst


class BasePipeline(object):

    # Return some value > 0 to stop the pipeline on that second
    def finish_time(self):
        return 0

    def build_pipeline(self, args):
        raise NotImplementedError

    def _build_capsfilter(self, caps_string):
        capsfilter = Gst.ElementFactory.make("capsfilter", None)
        capsfilter.set_property("caps", Gst.Caps(caps_string))
        return capsfilter

    def _mk_elem(self, name, properties=None):
        if properties is None:
            properties = {}
        new_elem = Gst.ElementFactory.make(name, None)
        for prop_name, prop_value in properties.items():
            new_elem.set_property(prop_name, prop_value)
        return new_elem

    def _link_all(self, elements):
        for index, elem in enumerate(elements[:-1]):
            elem.link(elements[index+1])


class TextOverlayPipeline(BasePipeline):

    def build_pipeline(self, args):
        text = args[0] if args else "Hola Claseeeeee!!!!"

        # build elements
        src = Gst.ElementFactory.make("videotestsrc", None)
        capsfilter = self._build_capsfilter("video/x-raw, width=720, height=576")
        textoverlay = Gst.ElementFactory.make("textoverlay", None)
        textoverlay.set_property("text", text)
        sink = Gst.ElementFactory.make("autovideosink", None)

        # build pipeline and add elements
        pipeline = Gst.Pipeline.new("my-pipeline")
        pipeline.add(src, capsfilter, textoverlay, sink)

        # link elements. Must be linked after being added
        src.link(textoverlay)
        textoverlay.link(capsfilter)
        capsfilter.link(sink)
        return pipeline


class EpilepsiaPipeline(BasePipeline):

    def build_pipeline(self, args):
        text = args[0] if args else "Hola Claseeeeee!!!!"

        # build elements
        src = Gst.ElementFactory.make("videotestsrc", None)
        src.set_property("pattern", 12)
        capsfilter = self._build_capsfilter("video/x-raw, width=720, height=576")
        textoverlay = Gst.ElementFactory.make("textoverlay", None)
        textoverlay.set_property("text", text)
        sink = Gst.ElementFactory.make("autovideosink", None)

        # build pipeline and add elements
        pipeline = Gst.Pipeline.new("my-pipeline")
        pipeline.add(src, capsfilter, textoverlay, sink)

        # link elements. Must be linked after being added
        src.link(textoverlay)
        textoverlay.link(capsfilter)
        capsfilter.link(sink)
        return pipeline


class AdaptativeStreamingPipeline(BasePipeline):

    def build_pipeline(self, args):
        # build elements
        src_elems = [
            self._mk_elem("v4l2src"),
            self._mk_elem("videoconvert"),
            self._mk_elem("tee")
        ]
        low_sink = self._mk_hls_sink("low", 200, 640, 360)
        high_sink = self._mk_hls_sink("high", 900, 960, 540)

        # Add elements to the pipeline
        pipeline = Gst.Pipeline.new("Adaptative-Streaming")
        pipeline.add(*src_elems)
        pipeline.add(*low_sink)
        pipeline.add(*high_sink)

        # link elements
        self._link_all(src_elems)
        self._link_all(low_sink)
        self._link_all(high_sink)
        tee = src_elems[-1]
        tee.link(low_sink[0])
        tee.link(high_sink[0])

        return pipeline

    def _mk_hls_sink(self, name, bitrate, width, height):
        return [
            self._mk_elem("textoverlay", {
                "text": "STREAM {}".format(name.upper()),
                "font-desc": "30"
            }),
            self._mk_elem("queue2"),
            self._mk_elem("videoscale"),
            self._build_capsfilter("video/x-raw, width={}, height={}".format(width, height)),
            self._mk_elem("x264enc", {"bitrate": bitrate}),
            self._mk_elem("mpegtsmux"),
            self._mk_elem("hlssink", {
                "target-duration": 2,
                "max-files": 10,
                "playlist-location": "{}.m3u8".format(name),
                "location": "segment_{}_%05d.ts".format(name)
            })
        ]



class CaptureScreenPipeline(BasePipeline):

    def __init__(self):
        self.seconds = 0
        self.profiles = {
            "high": {"pass": 4, "quantizer": 21, "speed-preset": "slow"},
            "mid": {"pass": 4, "quantizer": 26, "speed-preset": "fast"},
            "low": {"pass": 4, "quantizer": 35, "speed-preset": "ultrafast"}
        }

    def build_pipeline(self, args):
        x = int(args[0])
        y = int(args[1])
        w = int(args[2])
        h = int(args[3])
        profile = args[4]
        if len(args) > 5:
            self.seconds = int(args[5])
        if profile not in self.profiles:
            raise ValueError("Profile '{}' no existe".format(profile))

        # build elements
        src = Gst.ElementFactory.make("ximagesrc", None)
        src.set_property("startx", x)
        src.set_property("endx", x + w)
        src.set_property("starty", y)
        src.set_property("endy", y + h)
        src.set_property("use-damage", False)

        timeoverlay = Gst.ElementFactory.make("timeoverlay", None)
        timeoverlay.set_property("font-desc", "30")
        capsfilter = self._build_capsfilter("video/x-raw, framerate=25/1")
        buffer_1 = Gst.ElementFactory.make("queue2", None)
        buffer_2 = Gst.ElementFactory.make("queue2", None)
        convert = Gst.ElementFactory.make("videoconvert", None)

        encoder = Gst.ElementFactory.make("x264enc", "encoder")
        for enc_arg, enc_value in self.profiles[profile].items():
            encoder.set_property(enc_arg, enc_value)

        audiosrc = Gst.ElementFactory.make("filesrc", None)
        audiosrc.set_property("location", "input.mp3")
        audioparser = Gst.ElementFactory.make("mpegaudioparse", None)
        audiodec = Gst.ElementFactory.make("mad", None)
        audioconvert = Gst.ElementFactory.make("audioconvert", None)
        audioenc = Gst.ElementFactory.make("lamemp3enc", None)

        muxer = Gst.ElementFactory.make("matroskamux", "muxer")
        sink = Gst.ElementFactory.make("filesink", None)
        sink.set_property("location", "output.mkv")

        # build pipeline and add elements
        pipeline = Gst.Pipeline.new("my-pipeline")
        pipeline.add(src, capsfilter, timeoverlay, convert, buffer_1, encoder, muxer, buffer_2, sink,
            audiosrc, audioparser, audiodec, audioconvert, audioenc)
        # link elements. Must be linked after being added
        self._link_all([src, convert, capsfilter, timeoverlay, buffer_1, encoder, muxer, buffer_2, sink])
        self._link_all([audiosrc, audioparser, audiodec, audioconvert, audioenc, muxer])

        return pipeline

    def finish_time(self):
        return self.seconds
