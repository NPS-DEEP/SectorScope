import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramAnnotations():
    """Renders histogram annotation text in the histogram canvas based on
    registered events.
    """

    def __init__(self, canvas, x0, y0, w, h, histogram_dimensions,
                 bucket_width, identified_data, annotation_filter):

        self._canvas = canvas
        self._x0 = x0
        self._y0 = y0
        self._w = w
        self._h = h
        self._histogram_dimensions = histogram_dimensions
        self._bucket_width = bucket_width
        self._identified_data = identified_data
        self._annotation_filter = annotation_filter

        print("histogram_annotations", x0, y0, w, h)
        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive annotation filter change events
        annotation_filter.set_callback(self._handle_annotation_filter_change)

        # register to receive histogram dimensions change events
        self._histogram_dimensions.set_callback(
                                    self._handle_histogram_dimensions_change)

    def _load(self):
        # clear existing annotations from the canvas
        self._canvas.delete("annotations")

        # load annotations into the canvas
        c = self._canvas
        annotations = self._identified_data.annotations
        ignored_types = self._annotation_filter.ignored_types
        i=0
        for annotation_type, offset, length, text in annotations:
            # skip filtered out annotations
            if annotation_type in ignored_types:
                continue
            i+=1
            # load text
            c.create_text(0,0, justify=tkinter.LEFT, tags=("annotations",
                                                       "t%d" % i), text=text)

            # load line
            c.create_line(0,0,0,0, tags=("annotations", "l%d" % i))

    def _place(self):
        # place annotations
        c = self._canvas
        annotations = self._identified_data.annotations
        ignored_types = self._annotation_filter.ignored_types
        start_offset = self._histogram_dimensions.start_offset
        scale = self._histogram_dimensions.bytes_per_bucket * self._bucket_width
        i=0
        for annotation_type, offset, length, text in annotations:
            # skip filtered out annotations
            if annotation_type in ignored_types:
                continue
            i+=1
            # place text
            c.coords("t%d"%i, (offset - start_offset) * scale, 10)

            # place line
            c.coords("l%d"%i, (offset - start_offset) * scale, 10,
                              (offset + length - start_offset) * scale, 10)

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):
        # wait for annotation filter change instead
        self._load()
        self._place()

    # this function is registered to and called by AnnotationFilter
    def _handle_annotation_filter_change(self, *args):
        self._load()
        self._place()

    # this function is registered to and called by HistogramDimensions
    def _handle_histogram_dimensions_change(self, *args):
        self._place()

