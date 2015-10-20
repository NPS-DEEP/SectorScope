import colors
from sys import platform
from sys import maxsize
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from math import log, floor
from show_error import ShowError
from histogram_dimensions import HistogramDimensions
from histogram_data import HistogramData
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramBar():
    """Renders a hash histogram bar widget.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and move behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _hash_counts(dict of <hash, (count, is_ignored, is_highlighted)>):
        hash and calculated count tuple for each hash.
      _histogram_dimensions(HistogramDimensions): The start_offset,
        bytes_per_bucket, and associated bar dimension methods.

    Notes about offset alignment:
      The start and end offsets may be any value, even fractional.
      Bucket boundaries may be any value, even fractional.
      The cursor falls on bucket boundaries.
      Annotation can say that a bucket starts on a block boundary because
        block hash features align to block boundaries.
      Selection and range selection values round down to block boundary
    """
    # number of buckets across the bar
    NUM_BUCKETS = 220

    # pixels per bucket
    BUCKET_WIDTH = 3

    # bar size in pixels
    HISTOGRAM_BAR_WIDTH = NUM_BUCKETS * BUCKET_WIDTH
    HISTOGRAM_BAR_HEIGHT = 120

    # bar dimensions including start offset and scale
    _histogram_dimensions = HistogramDimensions(NUM_BUCKETS)

    # histogram data and the methods that calculate this data
    _histogram_data = HistogramData(NUM_BUCKETS)

    # cursor state
    _is_valid_cursor = False
    _cursor_offset = 0

    # mouse b1 left-click states
    _b1_pressed = False
    _b1_pressed_offset = 0

    # mouse b3 right-click states
    _b3_down_x = None
    _b3_dragged = False
    _b3_down_start_offset = None

    def __init__(self, master, identified_data, filters,
                                       range_selection, fit_range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
          fit_range_selection(FitRangeSelection): Receive signal to fit range.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._range_selection = range_selection

        # the photo_image
        self._photo_image = tkinter.PhotoImage(width=self.HISTOGRAM_BAR_WIDTH,
                                               height=self.HISTOGRAM_BAR_HEIGHT)
        self._photo_image.put("gray", to=(0, 0, self.HISTOGRAM_BAR_WIDTH,
                                                self.HISTOGRAM_BAR_HEIGHT))

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)
        self.frame.pack()

        # frame for bar statistics
        bar_statistics_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        bar_statistics_frame.pack(side=tkinter.TOP, anchor="w")

        # bucket width label
        self._bucket_width_label = tkinter.Label(bar_statistics_frame,
                                   anchor="w", width=40, bg=colors.BACKGROUND)
        self._bucket_width_label.pack(side=tkinter.LEFT, pady=(4,0))

        # bucket count label
        self._bucket_count_label = tkinter.Label(bar_statistics_frame,
                                   anchor="w", width=30, bg=colors.BACKGROUND)
        self._bucket_count_label.pack(side=tkinter.LEFT)

        # add the frame for offset values
        offsets_frame = tkinter.Frame(self.frame, height=18+0,
                                                         bg=colors.BACKGROUND)
        offsets_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        # leftmost offset value
        self._start_offset_label = tkinter.Label(offsets_frame,
                                                         bg=colors.BACKGROUND)
        self._start_offset_label.place(relx=0.0, anchor=tkinter.NW)

        # cursor offset value
        self._image_offset_label = tkinter.Label(offsets_frame,
                                                         bg=colors.BACKGROUND)
        self._image_offset_label.place(relx=0.5, anchor=tkinter.N)

        # rightmost offset value
        self._stop_offset_label = tkinter.Label(offsets_frame,
                                                         bg=colors.BACKGROUND)
        self._stop_offset_label.place(relx=1.0, anchor=tkinter.NE)

        # add the label containing the histogram bar PhotoImage
        l = tkinter.Label(self.frame, image=self._photo_image,
                                                relief=tkinter.SUNKEN, bd=1)
        l.pack(side=tkinter.TOP)

        # bind mouse motion and b1 events
        l.bind('<Motion>', self._handle_motion_and_b1_motion, add='+')
        l.bind('<Button-1>', self._handle_b1_press, add='+')
        l.bind('<ButtonRelease-1>', self._handle_b1_release, add='+')
        l.bind('<Enter>', self._handle_enter, add='+')
        l.bind('<Leave>', self._handle_leave, add='+')

        # bind mouse wheel events
        # https://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        l.bind("<MouseWheel>", self._handle_mouse_wheel, add='+')
        # with Linux OS
        l.bind("<Button-4>", self._handle_mouse_wheel, add='+')
        l.bind("<Button-5>", self._handle_mouse_wheel, add='+')

#        Tooltip(l, "Click to select offset\n"
#                   "Right-click drag to select region\n"
#                   "Left-click drag to pan\n"
#                   "Scroll to zoom")

        # bind mouse b3 right-click events
        if platform == 'darwin':
            # mac right-click is Button-2
            l.bind('<Button-2>', self._handle_b3_press, add='+')
            l.bind('<B2-Motion>', self._handle_b3_move, add='+')
            l.bind('<ButtonRelease-2>', self._handle_b3_release, add='+')
        else:
            # Linux, Win right-click is Button-3
            l.bind('<Button-3>', self._handle_b3_press, add='+')
            l.bind('<B3-Motion>', self._handle_b3_move, add='+')
            l.bind('<ButtonRelease-3>', self._handle_b3_release, add='+')

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # register to receive fit range selection change events
        fit_range_selection.set_callback(
                                    self._handle_fit_range_selection_change)

        # set to basic initial state
        self._handle_identified_data_change()

    # this function is registered to and called by Filters
    def _handle_filter_change(self, *args):

        # calculate this view
        self._histogram_data.calculate_hash_counts(
                                self._identified_data.hashes, self._filters)
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # draw
        self._draw()

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):

        # set dimensions for this image
        self._histogram_dimensions.fit_image(self._identified_data.image_size,
                                             self._identified_data.block_size)

        # calculate this view
        self._histogram_data.calculate_hash_counts(
                                self._identified_data.hashes, self._filters)
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # draw
        self._draw()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        # draw
        self._draw()

    # this function is registered to and called by FitRangeSelection
    def _handle_fit_range_selection_change(self, *args):
        self._fit_range()

    # redraw everything
    def _draw(self):
        self._draw_text()
        self._draw_clear()
        self._draw_range_selection()
        self._draw_buckets()
        self._draw_cursor_marker()

    def _draw_text(self):

        # bucket width
        self._bucket_width_label["text"] = "Bar width: %s" % \
                    offset_string(self._histogram_dimensions.bytes_per_bucket)
 
        # put in the offset start and stop text
        self._start_offset_label["text"] = offset_string(
                                      self._histogram_dimensions.start_offset)
        stop_offset = self._histogram_dimensions.start_offset + (
                               self._histogram_dimensions.bytes_per_bucket *
                                                          self.NUM_BUCKETS)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # cursor image offset
        if self._is_valid_cursor or self._b1_pressed:
            # cursor byte offset text
            self._image_offset_label["text"] = offset_string(
                                                         self._cursor_offset)
        else:
            # clear
            self._image_offset_label['text'] = ""

        # cursor bucket count
        if self._is_valid_cursor and \
                              self._histogram_dimensions.offset_is_on_bucket(
                                                        self._cursor_offset):
            # bucket count at cursor
            self._bucket_count_label["text"] = "Bar matches: %s" % \
                             self._histogram_data.source_buckets[ \
                             self._histogram_dimensions.offset_to_bucket(
                                                         self._cursor_offset)]
        else:
            # clear
            self._bucket_count_label['text'] = "Bar matches: Bar not selected"

    # clear everything
    def _draw_clear(self):

        # clear any previous content
        self._photo_image.put("white", to=(0,0,self.HISTOGRAM_BAR_WIDTH,
                                               self.HISTOGRAM_BAR_HEIGHT))

    # draw the range selection
    def _draw_range_selection(self):
        if self._range_selection.is_selected:

            # get bucket 1 value
            b1 = self._histogram_dimensions.offset_to_bucket(
                                           self._range_selection.start_offset)
            if b1 < 0: b1 = 0
            if b1 > self.NUM_BUCKETS: b1 = self.NUM_BUCKETS
            x1 = b1 * self.BUCKET_WIDTH

            # get bucket b2 value
            b2 = self._histogram_dimensions.offset_to_bucket(
                                           self._range_selection.stop_offset)
            if b2 < 0: b2 = 0
            if b2 > self.NUM_BUCKETS: b2 = self.NUM_BUCKETS
            x2 = b2 * self.BUCKET_WIDTH

            # keep range from becoming too narrow to plot
            if x2 == x1: x2 += 1

            # fill the range with the range selection color
            self._photo_image.put(colors.RANGE,
                                 to=(x1, 0, x2, self.HISTOGRAM_BAR_HEIGHT))

    # draw all the buckets
    def _draw_buckets(self):
        # skip empty initial-state data
        if self._histogram_dimensions.bytes_per_bucket == -1:
            return

        # valid bucket boundaries map inside the image
        leftmost_bucket, rightmost_bucket = \
                             self._histogram_dimensions.valid_bucket_range()

        # draw the buckets
        for bucket in range(self.NUM_BUCKETS):

            # calculate number of blocks in this bucket
            density = ((self._histogram_dimensions.bucket_to_offset(
                       bucket + 1) -
                       self._histogram_dimensions.bucket_to_offset(bucket)) /
                       self._identified_data.block_size)
            if density != int(density):
                print("ints", bucket,
                              self._histogram_dimensions.bucket_to_offset(
                                                                    bucket+1),
                              self._histogram_dimensions.bucket_to_offset(
                                                                      bucket),
                              self._identified_data.block_size)
                raise RuntimeError("program error")

            # bucket view depends on whether byte offset is in range
            if bucket >= leftmost_bucket and bucket <= rightmost_bucket:
                self._draw_bucket(bucket, density)
            else:
                self._draw_gray_bucket(bucket)

    """Calculate clipped bar height from count.
      Rationale for formula "int(log(count + 1, 1.23) * 2)" follows:
          * The scale should be as light as possible but still not clip.
          * A count of 1 should be 3 pixels tall so that the smallest unit is
            readily visible.
          * An arbitrarily chosen count of 200,000 should fully fill the
            arbitrarily chosen 60-pixel high bar.
    """
    def _bar_height(self, count, density):
#        h = int(log(count + 1, 1.1))
        h = int(count / density * 100)

        # make small value visible
        if h == 0 and count > 0:
            h = 1

        # clip to keep in range
        if h > int(self.HISTOGRAM_BAR_HEIGHT):
            h = int(self.HISTOGRAM_BAR_HEIGHT)

        return h

    # draw one bar for one bucket
    def _draw_bar(self, color, count, density, i):

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * self.BUCKET_WIDTH)
        y = self._bar_height(count, density)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             self.HISTOGRAM_BAR_HEIGHT,
             x+self.BUCKET_WIDTH,
             self.HISTOGRAM_BAR_HEIGHT - y))

    # draw one tick mark for one bucket, see draw_bar
    def _draw_tick(self, color, count, density, i):

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * self.BUCKET_WIDTH)
        y = self._bar_height(count, density)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             self.HISTOGRAM_BAR_HEIGHT - y + 1,
             x+self.BUCKET_WIDTH,
             self.HISTOGRAM_BAR_HEIGHT - y))

    # draw all bars for one bucket
    def _draw_bucket(self, i, density):

        # all sources with ignored sources removed: light blue bar
        self._draw_bar(colors.ALL_LIGHTER,
                    self._histogram_data.source_buckets[i] -
                    self._histogram_data.ignored_source_buckets[i], density, i)

        # all sources: light blue tick
        self._draw_tick(colors.ALL_LIGHTER,
                            self._histogram_data.source_buckets[i], density, i)

        # highlighted matches: light green bar
        self._draw_bar(colors.HIGHLIGHTED_LIGHTER,
                            self._histogram_data.highlighted_source_buckets[i],
                                                                    density, i)

    # draw one gray bucket for out-of-range data
    def _draw_gray_bucket(self, i):
        # x pixel coordinate
        x=(i * self.BUCKET_WIDTH)

        # out of range so fill bucket area gray
        self._photo_image.put("gray", to=(x, 0, x+self.BUCKET_WIDTH,
                                                  self.HISTOGRAM_BAR_HEIGHT))

    # draw the cursor marker
    def _draw_cursor_marker(self):
        if self._is_valid_cursor:
            x = self._histogram_dimensions.offset_to_bucket(
                                     self._cursor_offset) * self.BUCKET_WIDTH
            self._photo_image.put("red", to=(x, 0, x+1,
                                                  self.HISTOGRAM_BAR_HEIGHT))

    # convert mouse coordinate to bucket
    def _mouse_to_bucket(self, e):
        """Returns bucket number even if outside valid range."""
        # Note that e.x-1 is used because x is with respect to label,
        # not PhotoImage, and label has a 1-pixel border.
        return int((e.x - 1) / self.BUCKET_WIDTH)

    def _handle_enter(self, e):
        self._handle_motion_and_b1_motion(e)

    def _handle_leave(self, e):
        self._is_valid_cursor = False

        # note: could also set b1_pressed false because pop-up window blocks
        # b1 release, but doing so prevents drag outside bar, which is worse.

        # redraw
        self._draw()

    def _handle_b1_press(self, e):
        self._set_cursor(e)
        if self._is_valid_cursor:
            self._b1_pressed = True
            self._b1_pressed_offset = \
                                 self._histogram_dimensions.bucket_to_offset(
                                                    self._mouse_to_bucket(e))
            self._handle_motion_and_b1_motion(e)

    def _handle_motion_and_b1_motion(self, e):
        # set mouse cursor
        self._set_cursor(e)
        self._draw()

        # select range if b1 down
        if self._b1_pressed:
            self._range_selection.set(self.frame, self._identified_data,
                           self._b1_pressed_offset,
                           self._histogram_dimensions.bucket_to_offset(
                                                   self._mouse_to_bucket(e)))

    def _handle_b1_release(self, e):
        self._handle_motion_and_b1_motion(e)
        self._b1_pressed = False

    # pan start or right click
    def _handle_b3_press(self, e):
        self._b3_down_x = e.x
        self._b3_down_start_offset = self._histogram_dimensions.start_offset

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

    def _zoom_in(self):
        """zoom and then redraw."""

        # zoom in
        self._histogram_dimensions.zoom(self._cursor_offset, 0.67)

        # recalculate bucket data
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # redraw
        self._draw()

    def _zoom_out(self):
        """zoom and then redraw."""

        # zoom out
        self._histogram_dimensions.zoom(self._cursor_offset, 1.0 / 0.67)

        # recalculate bucket data
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # redraw
        self._draw()

    def _set_cursor(self, e):
        self._cursor_offset = self._histogram_dimensions.bucket_to_offset(
                                                     self._mouse_to_bucket(e))
        self._is_valid_cursor = self._histogram_dimensions.offset_is_on_graph(
                                                          self._cursor_offset)

    def _pan(self, start_offset_anchor, e):
        num_buckets = int((self._b3_down_x - e.x) / self.BUCKET_WIDTH)
        self._histogram_dimensions.pan(start_offset_anchor, num_buckets)

        # recalculate bucket data
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)
        self._draw()

    def _fit_range(self):
        self._histogram_dimensions.fit_range(
                                       self._range_selection.start_offset,
                                       self._range_selection.stop_offset)

        # recalculate bucket data
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # redraw
        self._draw()

    def fit_image(self):
        """Fit view to show whole media image."""
        self._histogram_dimensions.fit_image(self._image_size,
                                             self._identified_data.block_size)

        # recalculate bucket data
        self._histogram_data.calculate_bucket_data(
                                  self._identified_data.forensic_paths,
                                  self._histogram_dimensions.start_offset,
                                  self._histogram_dimensions.bytes_per_bucket)

        # redraw
        self._draw()

