import colors
from sys import platform
from sys import maxsize
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from math import log
from show_error import ShowError
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

    Notes about offset alignment:
      The start and end offsets may be any value, even fractional.
      Bucket boundaries may be any value, even fractional.
      The cursor falls on bucket boundaries.
      Annotation can say that a bucket starts on a sector boundary because
        block hash features align to sector boundaries.
      Selection and range selection values round to nearest sector boundary
    """
    # number of buckets across the bar
    NUM_BUCKETS = 220

    # pixels per bucket
    BUCKET_WIDTH = 3

    # bar size in pixels
    HISTOGRAM_BAR_WIDTH = NUM_BUCKETS * BUCKET_WIDTH
    HISTOGRAM_BAR_HEIGHT = 180 # make divisible by 3 so bar rows align

    # bar start offset and scale
    _start_offset = 0      # sector-aligned
    _bytes_per_bucket = 0   # may be fractional

    # cursor byte offset
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
        self.frame = tkinter.Frame(master, bg="blue")
        self.frame.pack()

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
        self._calculate_hash_counts()
        self._calculate_bucket_data()

        # draw
        self._draw()

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):

        # data constants
        self._image_size = self._identified_data.image_size
        self._sector_size = self._identified_data.sector_size

        # start fully zoomed out
        self._start_offset = 0
        self._bytes_per_bucket = self._image_size / self.NUM_BUCKETS

        # bytes per bucket may be fractional but not less than sector size
        # sector per bucket
        if self._bytes_per_bucket < self._sector_size:
            self._bytes_per_bucket = self._sector_size

        # calculate this view
        self._calculate_hash_counts()
        self._calculate_bucket_data()

        # draw
        self._draw()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        # draw
        self._draw()

    # this function is registered to and called by FitRangeSelection
    def _handle_fit_range_selection_change(self, *args):
        self._fit_range()

    def _calculate_hash_counts(self):

        # optimization: make local references to filter variables
        ignore_max_hashes = self._filters.ignore_max_hashes
        ignore_flagged_blocks = self._filters.ignore_flagged_blocks
        ignored_sources = self._filters.ignored_sources
        ignored_hashes = self._filters.ignored_hashes
        highlighted_sources = self._filters.highlighted_sources
        highlighted_hashes = self._filters.highlighted_hashes

        # calculate _hash_counts based on identified data
        # _hash_counts is dict<hash, (count, is_ignored, is_highlighted)>
        self._hash_counts = dict()
        for block_hash, (source_id_set, has_label) in \
                                         self._identified_data.hashes.items():
            count = len(source_id_set)
            is_ignored = False
            is_highlighted = False

            # count exceeds ignore_max_hashes
            if ignore_max_hashes != 0 and count > ignore_max_hashes:
                is_ignored = True

            # hash is ignored
            if block_hash in ignored_hashes:
                is_ignored = True

            # hash is highlighted
            if block_hash in highlighted_hashes:
                is_highlighted = True

            # flagged blocks are ignored
            if ignore_flagged_blocks and has_label:
                is_ignored = True

            # a source associated with this hash is ignored
            if len(ignored_sources.intersection(source_id_set)):
                is_ignored = True

            # a source associated with this hash is highlighted
            if len(highlighted_sources.intersection(source_id_set)):
                is_highlighted = True

            # set the count tuple for the hash
            self._hash_counts[block_hash] = (count, is_ignored, is_highlighted)

    def _calculate_bucket_data(self):
        """Buckets show hashes per bucket and sources per bucket.
        """
        # initialize empty buckets for each data type to plot
        self._hash_buckets = [0] * (self.NUM_BUCKETS)
        self._source_buckets = [0] * (self.NUM_BUCKETS)
        self._ignored_hash_buckets = [0] * (self.NUM_BUCKETS)
        self._ignored_source_buckets = [0] * (self.NUM_BUCKETS)
        self._highlighted_hash_buckets = [0] * (self.NUM_BUCKETS)
        self._highlighted_source_buckets = [0] * (self.NUM_BUCKETS)

        # calculate the histogram
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            bucket = int((offset - self._start_offset) // \
                                                   self._bytes_per_bucket)
            if bucket < 0 or bucket >= self.NUM_BUCKETS:
                # offset is out of range of buckets
                continue

            # set values for buckets
            count, is_ignored, is_highlighted = self._hash_counts[block_hash]

            # hash and source buckets
            self._hash_buckets[bucket] += 1
            self._source_buckets[bucket] += count

            # ignored hash and source buckets
            if is_ignored:
                self._ignored_hash_buckets[bucket] += 1
                self._ignored_source_buckets[bucket] += count

            # highlighted hash and source buckets
            if is_highlighted:
                self._highlighted_hash_buckets[bucket] += 1
                self._highlighted_source_buckets[bucket] += count

    # redraw everything
    def _draw(self):
        self._draw_text()
        self._draw_clear()
        self._draw_range_selection()
        self._draw_buckets()
        self._draw_separator_lines()
        self._draw_cursor_marker()

    def _draw_text(self):
 
        # put in the offset start and stop text
        self._start_offset_label["text"] = offset_string(self._start_offset)
        stop_offset = int(self._start_offset +
                          self._bytes_per_bucket * self.NUM_BUCKETS)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # put in the cursor byte offset text
        if self._is_valid_cursor:
            self._image_offset_label["text"] = offset_string(
                                                      self._cursor_offset)
        else:
            # clear
            self._image_offset_label['text'] = ""

    # clear everything
    def _draw_clear(self):

        # clear any previous content
        self._photo_image.put("white", to=(0,0,self.HISTOGRAM_BAR_WIDTH,
                                               self.HISTOGRAM_BAR_HEIGHT))

    # draw the range selection
    def _draw_range_selection(self):
        if self._range_selection.is_selected:

            # get bucket 1 value
            b1 = self._offset_to_bucket(self._range_selection.start_offset)
            if b1 < 0: b1 = 0
            if b1 > self.NUM_BUCKETS: b1 = self.NUM_BUCKETS
            x1 = b1 * self.BUCKET_WIDTH

            # get bucket b2 value
            b2 = self._offset_to_bucket(self._range_selection.stop_offset)
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
        if self._bytes_per_bucket == 0:
            return

        # valid bucket boundaries map inside the image
        leftmost_bucket = max(int(-(self._start_offset +
                                    self._bytes_per_bucket)) /
                                self._bytes_per_bucket, 0)
        rightmost_bucket = min(round((self._image_size - self._start_offset) /
                                self._bytes_per_bucket), self.NUM_BUCKETS)

        # draw the buckets
        for bucket in range(self.NUM_BUCKETS):

            # bucket view depends on whether byte offset is in range
            if bucket >= leftmost_bucket and bucket < rightmost_bucket:
                self._draw_bucket(bucket)
            else:
                self._draw_gray_bucket(bucket)

    # draw the horizontal separator lines between the three bucket groups
    def _draw_separator_lines(self):

        # draw the lines
        for i in (1,2):
            y = int(self.HISTOGRAM_BAR_HEIGHT / 3 * i)
            self._photo_image.put("black",
                                  to=(0, y-1, self.HISTOGRAM_BAR_WIDTH, y))

    """Calculate clipped bar height from count.
      Rationale for formula "int(log(count + 1, 1.23) * 2)" follows:
          * The scale should be as light as possible but still not clip.
          * A count of 1 should be 3 pixels tall so that the smallest unit is
            readily visible.
          * An arbitrarily chosen count of 200,000 should fully fill the
            arbitrarily chosen 60-pixel high bar.
    """
    def _bar_height(self, count):
        h = int(log(count + 1, 1.5) * 2)

        # clip to keep in range
        if h > int(self.HISTOGRAM_BAR_HEIGHT / 3):
            h = int(self.HISTOGRAM_BAR_HEIGHT / 3)

        return h

    # draw one bar for one bucket
    def _draw_bar(self, color, count, i, j):
        # i is bucket number
        # j is bar row number, either 2, 1, or 0

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * self.BUCKET_WIDTH)
        y0 = int(self.HISTOGRAM_BAR_HEIGHT / 3 * j)
        y1 = self._bar_height(count)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             self.HISTOGRAM_BAR_HEIGHT - y0,
             x+self.BUCKET_WIDTH,
             self.HISTOGRAM_BAR_HEIGHT - (y0 + y1)))

    # draw one tick mark for one bucket, see draw_bar
    def _draw_tick(self, color, count, i, j):
        # i is bucket number
        # j is bar row number, either 2, 1, or 0

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * self.BUCKET_WIDTH)
        y0 = int(self.HISTOGRAM_BAR_HEIGHT / 3 * j)
        y1 = self._bar_height(count)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             self.HISTOGRAM_BAR_HEIGHT - (y0 + y1 - 1),
             x+self.BUCKET_WIDTH,
             self.HISTOGRAM_BAR_HEIGHT - (y0 + y1)))

    # draw all bars for one bucket
    def _draw_bucket(self, i):

        # draw bars #rrggbb

        # top bar: all matches and ignored matches removed

        # 1 all sources with ignored sources removed: light blue bar
        self._draw_bar(colors.ALL_LIGHTER, self._source_buckets[i] -
                                        self._ignored_source_buckets[i], i, 2)

        # 2 all hashes with ignored hashes removed: dark blue bar
        self._draw_bar(colors.ALL_DARKER, self._hash_buckets[i] -
                                        self._ignored_hash_buckets[i], i, 2)

        # 3 all sources: light blue tick
        self._draw_tick(colors.ALL_LIGHTER, self._source_buckets[i], i, 2)

        # 4 all hashes: dark blue tick
        self._draw_tick(colors.ALL_DARKER, self._hash_buckets[i], i, 2)

        # middle bar: highlighted matches: light, dark green
        self._draw_bar(colors.HIGHLIGHTED_LIGHTER,
                                    self._highlighted_source_buckets[i], i, 1)
        self._draw_bar(colors.HIGHLIGHTED_DARKER,
                                    self._highlighted_hash_buckets[i], i, 1)

        # bottom bar: ignored matches: light, dark red
        self._draw_bar(colors.IGNORED_LIGHTER,
                                    self._ignored_hash_buckets[i], i, 0)
        self._draw_bar(colors.IGNORED_DARKER,
                                    self._ignored_source_buckets[i], i, 0)

    # draw one gray bucket for out-of-range data
    def _draw_gray_bucket(self, i):
        # x pixel coordinate
        x=(i * self.BUCKET_WIDTH)

        # out of range so fill bucket area gray
        self._photo_image.put("gray", to=(x, 0, x+self.BUCKET_WIDTH,
                                                  self.HISTOGRAM_BAR_HEIGHT))

    # draw the cursor marker
    def _draw_cursor_marker(self):
        # cursor marker when valid and not selecting a range
        if self._is_valid_cursor:
            x = self._offset_to_bucket(self._cursor_offset) * self.BUCKET_WIDTH
            if x >= 0 and x < self.HISTOGRAM_BAR_WIDTH:
                self._photo_image.put("red",
                                      to=(x, 0, x+1, self.HISTOGRAM_BAR_HEIGHT))

    # sector alignment
    def _sector_align(self, offset):
        # round down to sector boundary
        try:
            return int(offset - offset % self._sector_size)
        except ZeroDivisionError:
            # not initialized
            return 0

    # convert mouse coordinate to aligned offset
    def _x_to_aligned_offset(self, x):
        bucket = x // self.BUCKET_WIDTH
        offset = int(self._start_offset + self._bytes_per_bucket * bucket)

        # put bounds on offset
        if offset < 0:
            offset = 0
        if offset > self._image_size:
            offset = self._image_size

        # align the offset
        return self._sector_align(offset)

    # convert byte offset to bucket
    def _offset_to_bucket(self, image_offset):
        bucket = int(round((image_offset - self._start_offset) /
                                                    self._bytes_per_bucket))
        return bucket

    # see if the given offset is within the media image range
    def _in_image_range(self, offset):
        return offset >= 0 and offset < self._image_size

    def _handle_enter(self, e):
        self._handle_motion_and_b1_motion(e)

    def _handle_leave(self, e):
        self._is_valid_cursor = False

        # note: could also set b1_pressed false because pop-up window blocks
        # b1 release, but doing so prevents drag outside bar, which is worse.

        # redraw
        self._draw()

    def _handle_b1_press(self, e):
        self._b1_pressed = True
        self._b1_pressed_offset = self._x_to_aligned_offset(e.x)
        self._handle_motion_and_b1_motion(e)

    def _handle_motion_and_b1_motion(self, e):
        # set mouse cursor
        self._set_cursor(e)
        self._draw()

        # select range if b1 down
        if self._b1_pressed:
            self._range_selection.set(self.frame, self._identified_data,
                                      self._b1_pressed_offset,
                                      self._x_to_aligned_offset(e.x))

    def _handle_b1_release(self, e):
        self._handle_motion_and_b1_motion(e)
        self._b1_pressed = False

    # pan start or right click
    def _handle_b3_press(self, e):
        self._b3_down_x = e.x
        self._b3_down_start_offset = self._start_offset

    # pan move
    def _handle_b3_move(self, e):
        self._pan(self._b3_down_start_offset, int((self._b3_down_x - e.x) /
                                                         self.BUCKET_WIDTH))
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
        self._zoom(0.67)

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def _zoom_out(self):
        """zoom and then redraw."""

        # zoom out
        self._zoom(1.0 / 0.67)

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def _set_cursor(self, e):
        self._cursor_offset = self._x_to_aligned_offset(e.x)
        self._is_valid_cursor = self._in_image_range(self._cursor_offset)

    def _zoom(self, ratio):
        """Recalculate start offset and bytes per bucket."""

        # get the zoom origin bucket
        zoom_origin_bucket = self._offset_to_bucket(self._cursor_offset)

        # calculate the new bytes per bucket
        new_bytes_per_bucket = self._bytes_per_bucket * (ratio)

        # do not let bytes per bucket get less than sector size
        if new_bytes_per_bucket < self._sector_size:
            new_bytes_per_bucket = self._sector_size

        # calculate the new start offset
        new_start_offset = self._sector_align(self._cursor_offset -
                                 new_bytes_per_bucket * zoom_origin_bucket)

        if not self._outside_graph(new_start_offset, new_bytes_per_bucket):
           self._start_offset = new_start_offset
           self._bytes_per_bucket = new_bytes_per_bucket

    def _outside_graph(self, start_offset, bytes_per_bucket):
        # media image is outside range of graph
        end_offset = start_offset + bytes_per_bucket * self.NUM_BUCKETS
        return start_offset > self._image_size or end_offset < 0

    def _pan(self, start_offset_anchor, dx):
        """Pan dx buckets based on the start_offset_anchor."""
        # pan
        new_start_offset = self._sector_align(start_offset_anchor +
                                                self._bytes_per_bucket * dx)

        if not self._outside_graph(new_start_offset, self._bytes_per_bucket):
            # accept the pan
            self._start_offset = new_start_offset

            # recalculate bucket data
            self._calculate_bucket_data()
            self._draw()

    def _fit_range(self):
        """Fit view to range selection."""
        # get start_offset and stop_offset range
        start_offset = self._range_selection.start_offset
        stop_offset = self._range_selection.stop_offset

        new_bytes_per_bucket = (stop_offset - start_offset) / self.NUM_BUCKETS

        # do not let bytes per pixel get too small
        if new_bytes_per_bucket < self._sector_size:
            new_bytes_per_bucket = self._sector_size

        # calculate the new start offset
        new_start_offset = start_offset

        self._start_offset = new_start_offset
        self._bytes_per_bucket = new_bytes_per_bucket

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def fit_image(self):
        """Fit view to show whole media image."""
        # initial zoomed-out position variables
        self._start_offset = 0
        self._bytes_per_bucket = self._image_size / self.NUM_BUCKETS

        # bytes per pixel may be fractional but not less than one
        # sector per bucket
        if self._bytes_per_bucket < self._sector_size:
            self._bytes_per_bucket = self._sector_size

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

