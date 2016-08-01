import colors
import histogram_constants
from sys import platform
from sys import maxsize
from forensic_path import offset_string, size_string, int_string
from icon_path import icon_path
from tooltip import Tooltip
from math import log, floor, log10, pow, ceil
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramControl():
    """Provides histogram events based on histogram control including
      mouse events and control functions.

    Attributes:
      change_type(str): plot_region_changed, cursor_moved, range_changed.
      media_size(int): Media size to bind motion events within.
      sector_size(int): Sector size of view.
      num_buckets(int): Number of buckets shown in the histogram.
      _histogram_mouse_changed is used as a signal.  Its value is always true.
    """

    # histogram dimensions
    num_buckets = 0
    histogram_bar_width = 0
    canvas_width = 0

    # change type signaled: plot_region_changed, cursor_moved, range_changed
    change_type = ""

    # sizes
    media_size = 0
    sector_size = 0

    # plot region
    start_offset = 0
    bytes_per_bucket = 0

    # cursor
    is_valid_cursor = False
    cursor_offset = 0

    # range
    is_valid_range = False
    range_start = 0
    range_stop = 0

    # mouse b1 left-click states
    _b1_pressed = False
    _b1_pressed_offset = 0

    # mouse b3 right-click states
    _b3_down_x = None
    _b3_dragged = False
    _b3_down_start_offset = None

    # runtime state
    _did_bind = False

    def __init__(self):
        self._histogram_mouse_changed = tkinter.BooleanVar()
        self.set_width(320)

    def __repr__(self):
        return "HistogramControl(change_type=%s, media_size=%d, " \
               "sector_size=%d, num_buckets=%d, " \
               "histogram_bar_width=%d, canvas_width=%d, "\
               "start_offset=%d, " \
               "bytes_per_bucket=%d, is_valid_cursor=%s, " \
               "cursor_offset=%d, is_valid_range=%s, " \
               "range_start=%d, range_stop=%d)" % (self.change_type,
                self.media_size, self.sector_size, self.num_buckets,
                self.histogram_bar_width, self.canvas_width,
                self.start_offset, self.bytes_per_bucket,
                self.is_valid_cursor, self.cursor_offset,
                self.is_valid_range, self.range_start, self.range_stop)

    def set_width(self, num_buckets):
        self.num_buckets = num_buckets
        self.histogram_bar_width = self.num_buckets * \
                                   histogram_constants.BUCKET_WIDTH
        self.canvas_width = self.histogram_bar_width + \
                                   histogram_constants.HISTOGRAM_X_OFFSET + 1
        self._fire_change("width_changed")

    def set_initial_view(self, media_size, sector_size):
        """Establish starting bounds, zoom fully out, and clear any range
          without firing any events."""
        # set constants given a scan dataset
        self.media_size = media_size
        self.sector_size = sector_size

        # zoom fully out
        self.start_offset = 0
        self.bytes_per_bucket = self._round_up_to_block(
                                          self.media_size / self.num_buckets)

        # clear any selected range
        self.is_valid_range = False
        self.range_start = 0
        self.range_stop = 0

    def bind_mouse(self, canvas):
        # only call once
        if self._did_bind:
            raise RuntimeError("program error")
        self._did_bind = True

        # bind mouse motion and b1 events
        canvas.bind('<Motion>', self._handle_motion_and_b1_motion, add='+')
        canvas.bind('<Button-1>', self._handle_b1_press, add='+')
        canvas.bind('<ButtonRelease-1>', self._handle_b1_release, add='+')
        canvas.bind('<Enter>', self._handle_enter, add='+')
        canvas.bind('<Leave>', self._handle_leave, add='+')

        # bind mouse wheel events
        # https://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        canvas.bind("<MouseWheel>", self._handle_mouse_wheel, add='+')
        # with Linux OS
        canvas.bind("<Button-4>", self._handle_mouse_wheel, add='+')
        canvas.bind("<Button-5>", self._handle_mouse_wheel, add='+')

        # bind mouse b3 right-click events
        if platform == 'darwin':
            # mac right-click is Button-2
            canvas.bind('<Button-2>', self._handle_b3_press, add='+')
            canvas.bind('<B2-Motion>', self._handle_b3_move, add='+')
            canvas.bind('<ButtonRelease-2>', self._handle_b3_release, add='+')
        else:
            # Linux, Win right-click is Button-3
            canvas.bind('<Button-3>', self._handle_b3_press, add='+')
            canvas.bind('<B3-Motion>', self._handle_b3_move, add='+')
            canvas.bind('<ButtonRelease-3>', self._handle_b3_release, add='+')
 
    def set_callback(self, f):
        """Register function f to be called on histogram mouse change."""
        self._histogram_mouse_changed.trace_variable('w', f)

    # ############################################################
    # mouse handlers
    # ############################################################
    def _handle_motion_and_b1_motion(self, e):
        if self._b1_pressed:
            # set cursor variables
            self.cursor_offset = self.bucket_to_offset(self._mouse_to_bucket(e))
            self.is_valid_cursor = self.offset_is_on_graph(self.cursor_offset)

            # select range
            self._set_range(self._b1_pressed_offset, self.bucket_to_offset(
                                                   self._mouse_to_bucket(e)))

        else:
            # just set mouse cursor
            self._set_cursor(e)

    def _handle_b1_press(self, e):
        self._set_cursor(e)
        if self.is_valid_cursor:
            self._b1_pressed = True
            self._b1_pressed_offset = self.bucket_to_offset(
                                                    self._mouse_to_bucket(e))
            self._handle_motion_and_b1_motion(e)

    def _handle_b1_release(self, e):
        self._handle_motion_and_b1_motion(e)
        self._b1_pressed = False

    def _handle_enter(self, e):
        self._handle_motion_and_b1_motion(e)

    def _handle_leave(self, e):
        self.is_valid_cursor = False

        # note: could also set b1_pressed false because pop-up window blocks
        # b1 release, but doing so prevents drag outside bar, which is worse.

        self._fire_change("cursor_moved")

    def _handle_mouse_wheel(self, e):
        # drag, so no action
        if self._b1_pressed:
            return

        # zoom
        if e.num == 4 or e.delta == 120:
            self._zoom_in()
        elif e.num == 5 or e.delta == -120:
            self._zoom_out()
        else:
            print("Unexpected _mouse_wheel")

    # pan start or right click
    def _handle_b3_press(self, e):
        self._b3_down_x = e.x
        self._b3_down_start_offset = self.start_offset

    # pan move
    def _handle_b3_move(self, e):
        self._pan(self._b3_down_start_offset, e)
        self._b3_dragged = True

    # pan stop or right click
    def _handle_b3_release(self, e):
        if self._b3_dragged:
            # end b3 pan motion
            self._b3_dragged = False

        else:
            # right click so no action
            pass

    # ############################################################
    # support
    # ############################################################
    # convert mouse coordinate to bucket
    def _mouse_to_bucket(self, e):
        """Returns bucket number even if outside valid range."""
        return int((e.x - histogram_constants.HISTOGRAM_X_OFFSET) /
                                           histogram_constants.BUCKET_WIDTH)

    # convert bucket to offset at left edge of bucket
    def bucket_to_offset(self, bucket):
        offset = self.start_offset + self.bytes_per_bucket * bucket
        return offset

    # convert offset to a bucket number
    def offset_to_bucket(self, media_offset):

        # initialization
        if self.bytes_per_bucket == 0:
            return -1

        # calculate bucket
        bucket = (media_offset - self.start_offset) // self.bytes_per_bucket

        return bucket

    def offset_is_on_graph(self, offset):
        """ the offset maps onto a bucket or to one past the last bucket."""
        # allow one bucket past last bucket
        bucket = self.offset_to_bucket(offset)
        return (bucket >= 0 and bucket <= self.num_buckets and
                bucket >= self.offset_to_bucket(0) and
                bucket <= self.offset_to_bucket(self._round_up_to_block(
                                                   self.media_size - 1)) + 1)

    def offset_is_on_bucket(self, offset):
        """ the offset maps onto a bucket."""
        # offset maps to a bucket
        bucket = self.offset_to_bucket(offset)
        return (bucket >= 0 and bucket < self.num_buckets and
                bucket >= self.offset_to_bucket(0) and
                bucket <= self.offset_to_bucket(self._round_up_to_block(
                                                       self.media_size - 1)))

    def valid_bucket_range(self):
        leftmost_bucket = self.offset_to_bucket(0)
        rightmost_bucket = self.offset_to_bucket(
                                 self._round_up_to_block(self.media_size -1))
        return leftmost_bucket, rightmost_bucket

    # round up to aligned block
    def _round_up_to_block(self, size):
        # not initialized
        if self.sector_size == 0:
            return 0

        # fix decimal limitation and get as int
        size = int(floor(round(size, 5)))

        # align
        if size % self.sector_size == 0:
            # already aligned
            return size

        else:
            # round up
            size += self.sector_size - (size % self.sector_size)
            return size

    # round down to aligned block
    def _round_down_to_block(self, size):

        # fix decimal limitation and get as int
        size = int(floor(round(size, 5)))

        # align
        if self.sector_size == 0 or size % self.sector_size == 0:
            # not initialized or already aligned
            return size

        else:
            # round down
            size -= size % self.sector_size
            return size

    def _inside_graph(self, proposed_start_offset, proposed_bytes_per_bucket):
        # the provided range is at least partially within the graph
        end_offset = proposed_start_offset + proposed_bytes_per_bucket * \
                                                          self.num_buckets
        return proposed_start_offset <= self.media_size and end_offset >= 0

    def bound_offset(self, offset):
        # return offset bound within range of media image
        if offset < 0:
            return 0
        if offset >= self.media_size:
            if self.media_size == 0:
                return 0
            else:
                return self.media_size - 1
        return offset

    def _fire_change(self, change_type):
        self.change_type = change_type
        self._histogram_mouse_changed.set(True)

    # ############################################################
    # plot region changed
    # ############################################################
    def _set_plot_region(self, new_start_offset, new_bytes_per_bucket):
        self.start_offset = new_start_offset
        self.bytes_per_bucket = new_bytes_per_bucket
        self._fire_change("plot_region_changed")

    def fit_media(self):
        self._set_plot_region(0, self._round_up_to_block(
                                         self.media_size / self.num_buckets))

    def fit_range(self):
        """Fit view to range selection."""

        # If unable to expand range to whole bar place range nicely
        # inside bar, see zoom() for math.

        # calculate the range center offset
        range_center_offset = self._round_up_to_block(
                                    (self.range_start + self.range_stop) / 2)

        # calculate the bucket at the range center
        range_center_bucket = self.offset_to_bucket(range_center_offset)

        # calculate the new bytes per bucket
        new_bytes_per_bucket = self._round_up_to_block(
                    (self.range_stop - self.range_start) / self.num_buckets)

        # calculate the new start offset
        new_range_start = range_center_offset - \
                                 new_bytes_per_bucket * range_center_bucket

        # set to left edge if too far left
        if self.range_start < new_range_start:
            new_range_start = self.range_start

        # set to right edge if too far right
        new_range_stop = new_range_start + \
                                      new_bytes_per_bucket * self.num_buckets
        if self.range_stop > new_range_stop:
            new_range_start = new_range_start - \
                              (new_range_stop - self.range_stop)

        # set the new values
        self._set_plot_region(new_range_start, new_bytes_per_bucket)

    def _pan(self, start_offset_anchor, e):
        num_pan_buckets = int((self._b3_down_x - e.x) /
                                            histogram_constants.BUCKET_WIDTH)
        new_start_offset = start_offset_anchor + self.bytes_per_bucket * \
                                                              num_pan_buckets

        if self._inside_graph(new_start_offset, self.bytes_per_bucket):
            # accept the pan
            self._set_plot_region(new_start_offset, self.bytes_per_bucket)

    def _zoom_in(self):
        """zoom and then redraw."""

        # zoom in
        self._zoom(0.67)

    def _zoom_out(self):
        """zoom and then redraw."""

        # zoom out
        self._zoom(1.0 / 0.67)

    def _zoom(self, ratio):
        """Recalculate start offset and bytes per bucket."""

        # get the zoom origin bucket
        zoom_origin_bucket = self.offset_to_bucket(self.cursor_offset)

        # calculate the new bytes per bucket
        if ratio < 1:
            # round down to ensure zooming in
            new_bytes_per_bucket = self._round_down_to_block(
                                             self.bytes_per_bucket * (ratio))

        else:
            # round up to ensure zooming out
            new_bytes_per_bucket = self._round_up_to_block(
                                             self.bytes_per_bucket * (ratio))

        # do not let bytes per bucket reach zero
        if new_bytes_per_bucket == 0:
            new_bytes_per_bucket = self.sector_size

        # calculate the new start offset
        new_start_offset = (self._round_down_to_block(self.cursor_offset -
                                   new_bytes_per_bucket * zoom_origin_bucket))

        if self._inside_graph(new_start_offset, new_bytes_per_bucket):
            # accept the zoom
            self._set_plot_region(new_start_offset, new_bytes_per_bucket)

    # ############################################################
    # cursor moved
    # ############################################################
    def _set_cursor(self, e):
        offset = self.bucket_to_offset(self._mouse_to_bucket(e))
        valid_cursor = self.offset_is_on_graph(offset)

        # accept the cursor change
        if offset != self.cursor_offset or valid_cursor != self.is_valid_cursor:
            self.cursor_offset = offset
            self.is_valid_cursor = valid_cursor
            self._fire_change("cursor_moved")

    # ############################################################
    # range changed
    # ############################################################
    def clear_range(self):
        self.is_valid_range = False
        self.range_start = 0
        self.range_stop = 0
        self._fire_change("range_changed")

    def _set_range(self, offset1, offset2):
        """Set offsets.  Input can be out of order.  Equal offsets clears."""

        # clear if no range
        if offset1 == offset2 or offset1 == offset2 + 1:
            self.clear_range()
            return

        # set range_start, range_stop
        if offset1 < offset2:
            start = offset1
            stop = offset2
        else:
            start = offset2
            stop = offset1

        # bound range to media image
        if start < 0:
            start = 0
        if stop > self.media_size:
            stop = self.media_size

        # accept the range change
        if not self.is_valid_range or start != self.range_start or \
                                     stop != self.range_stop:
            self.is_valid_range = True
            self.range_start = start
            self.range_stop = stop

            # signal change
            self._fire_change("range_changed")

