import colors
import histogram_constants
from sys import platform
from sys import maxsize
from forensic_path import offset_string, size_string, int_string
from icon_path import icon_path
from tooltip import Tooltip
from math import log, floor, log10, pow, ceil
from histogram_annotations import HistogramAnnotations
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramBar():
    """Renders a hash histogram bar widget.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and pan behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _histogram_control(HistogramControl): The start_offset,
        bytes_per_bucket, and associated bar dimension methods.
      _hash_counts(map<hash, (count, is_ignored, is_highlighted)>):
        Cached from and used by data_manager.
      _valid_bucket_range(tuple(first, last)): Vaid bucket endpoints.

    Notes about offset alignment:
      The start and end offsets may be any value, even fractional.
      Bucket boundaries may be any value, even fractional.
      The cursor falls on bucket boundaries.
      Annotation can say that a bucket starts on a block boundary because
        block hash features align to block boundaries.
      Selection and range selection values round down to block boundary
    """

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

    def __init__(self, master, data_manager,
                fit_range_selection, preferences,
                annotation_filter, histogram_control):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
          fit_range_selection(FitRangeSelection): Receive signal to fit range.
          preferences(Preferences): Preference, namely the offset format.
          annotation_filter(AnnotationFilter): The annotation filter that
            selections modify.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
        """

        # data variables
        self._data_manager = data_manager
        self._preferences = preferences
        self._annotation_filter = annotation_filter

        # control
        self._histogram_control = histogram_control

        # the photo_image
        self._photo_image = tkinter.PhotoImage(
                            width=self._histogram_control.histogram_bar_width,
                            height=histogram_constants.HISTOGRAM_BAR_HEIGHT)
        self._photo_image.put("gray", to=(0, 0,
                                 self._histogram_control.histogram_bar_width,
                                 histogram_constants.HISTOGRAM_BAR_HEIGHT))

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)
        self.frame.pack()

        # frame for bar statistics
        bar_statistics_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        bar_statistics_frame.pack(side=tkinter.TOP, anchor="w", pady=4)

        # bucket width label
        self._bucket_width_label = tkinter.Label(bar_statistics_frame,
                                   anchor="w", width=20, bg=colors.BACKGROUND)
        self._bucket_width_label.pack(side=tkinter.LEFT)

        # bucket count label
        self._bucket_count_label = tkinter.Label(bar_statistics_frame,
                                   anchor="w", width=35, bg=colors.BACKGROUND)
        self._bucket_count_label.pack(side=tkinter.LEFT)

        # range selection label
        self._range_selection_label = tkinter.Label(bar_statistics_frame,
                                   anchor="w", width=40, bg=colors.BACKGROUND)
        self._range_selection_label .pack(side=tkinter.LEFT)

        # add the canvas containing the histogram graph
        self._c = tkinter.Canvas(self.frame, relief=tkinter.SUNKEN,
                              width=self._histogram_control.canvas_width,
                              height=histogram_constants.CANVAS_HEIGHT, bd=0,
                              highlightthickness=0, bg=colors.BACKGROUND)
        self._c.pack(side=tkinter.TOP)

        # bind canvas mouse events to histogram control
        histogram_control.bind_mouse(self._c)

        # add a box to house the histogram
        self._c.create_rectangle(histogram_constants.HISTOGRAM_X_OFFSET-1,
                                    histogram_constants.HISTOGRAM_Y_OFFSET-1,
                                    histogram_constants.HISTOGRAM_X_OFFSET+0 +
                                    self._histogram_control.histogram_bar_width,
                                    histogram_constants.HISTOGRAM_Y_OFFSET+0 +
                                    histogram_constants.HISTOGRAM_BAR_HEIGHT,
                   outline=colors.BOUNDING_BOX)

        # add the histogram photo_image to the canvas
        self._c.create_image(histogram_constants.HISTOGRAM_X_OFFSET,
                             histogram_constants.HISTOGRAM_Y_OFFSET,
                             anchor=tkinter.NW, image=self._photo_image)

        # start offset
        self._start_offset_id = self._c.create_text(
                                      histogram_constants.HISTOGRAM_X_OFFSET,
                                      0, anchor=tkinter.NW)

        # cursor offset
        self._cursor_offset_id = self._c.create_text(
                         histogram_constants.HISTOGRAM_X_OFFSET +
                         self._histogram_control.histogram_bar_width // 2,
                         0, anchor=tkinter.N)

        # stop offset
        self._stop_offset_id = self._c.create_text(
                             histogram_constants.HISTOGRAM_X_OFFSET +
                             self._histogram_control.histogram_bar_width,
                             0, anchor=tkinter.NE)

        # y axis gradient mark 1
        x = histogram_constants.HISTOGRAM_X_OFFSET
        y = histogram_constants.HISTOGRAM_Y_OFFSET + \
                              histogram_constants.HISTOGRAM_BAR_HEIGHT - \
                              1 *histogram_constants.BUCKET_HEIGHT_MULTIPLIER
        self._c.create_line(x-8,y,x,y, fill=colors.BOUNDING_BOX)
        self._marker1_id = self._c.create_text(x-9, y, anchor=tkinter.E)

        # y axis gradient mark 2
        x = histogram_constants.HISTOGRAM_X_OFFSET
        y = histogram_constants.HISTOGRAM_Y_OFFSET + \
                             histogram_constants.HISTOGRAM_BAR_HEIGHT - \
                             10 *histogram_constants.BUCKET_HEIGHT_MULTIPLIER
        self._c.create_line(x-8,y,x,y, fill=colors.BOUNDING_BOX)
        self._marker2_id = self._c.create_text(x-9, y, anchor=tkinter.E)

        # y axis gradient mark 3
        x = histogram_constants.HISTOGRAM_X_OFFSET
        y = histogram_constants.HISTOGRAM_Y_OFFSET + \
                            histogram_constants.HISTOGRAM_BAR_HEIGHT - \
                            100 *histogram_constants.BUCKET_HEIGHT_MULTIPLIER
        self._c.create_line(x-8,y,x,y, fill=colors.BOUNDING_BOX)
        self._marker3_id = self._c.create_text(x-9, y, anchor=tkinter.E)

        # create the histogram annotations renderer which is fully event driven
        x0 = histogram_constants.HISTOGRAM_X_OFFSET
        y0 = histogram_constants.HISTOGRAM_Y_OFFSET + \
                                      histogram_constants.HISTOGRAM_BAR_HEIGHT
        w = self._histogram_control.num_buckets * \
                                      histogram_constants.BUCKET_WIDTH
        h = histogram_constants.ANNOTATION_HEIGHT
        self._histogram_annotations = HistogramAnnotations(self._c,
                      x0, y0, w, h, self._histogram_control,
                      self._data_manager, annotation_filter)

        # register to receive data manager change events
        data_manager.set_callback(self._handle_data_manager_change)

        # register to receive fit range change events
        fit_range_selection.set_callback(self._handle_fit_range_selection)

        # register to receive preferences change events
        preferences.set_callback(self._handle_preferences_change)

        # register to receive histogram control change events
        self._histogram_control.set_callback(
                                    self._handle_histogram_control_change)

        # set to basic initial state
        self._draw("data_changed")

    def _calculate_bucket_data(self):
        (self._source_buckets, self._ignored_source_buckets,
         self._highlighted_source_buckets, self._y_scale) = \
                      self._data_manager.calculate_bucket_data(
                                    self._hash_counts,
                                    self._histogram_control.start_offset,
                                    self._histogram_control.bytes_per_bucket,
                                    self._histogram_control.num_buckets)

    # this function is registered to and called by HistogramControl
    def _handle_histogram_control_change(self, *args):
        # cursor_moved, range_changed, plot_region_changed
        self._draw(self._histogram_control.change_type)

    # this function is registered to and called by Preferences
    def _handle_preferences_change(self, *args):
        # preferences_changed
        self._draw("preferences_changed")

    # this function is registered to and called by FitRangeSelection
    def _handle_fit_range_selection(self, *args):
        # fit_range
        self._draw("fit_range")

    # this function is registered to and called by the data manager
    def _handle_data_manager_change(self, *args):
        # data_changed or filter_changed
        self._draw(self._data_manager.change_type)

    def _draw(self, change_mode):
        """Draw text based on change mode, then redraw the graph.
        Change modes:
          cursor_moved: Cursor moved, redraw cursor bar and cursor
            offset text.
          range_changed: Range changed, recalculate sources in range,
            draw range rectangle and fire change for redrawing the
            sources table.
          plot_region_changed: Histogram zoomed or panned, redraw bars and
            annotation.
          fit_range: Redraw to fit range.
          preferences_changed: Offset text units changed, change annotation.
          plot_region_changed: Recalculate bucket counts due to pan or zoom
            and redraw buckets.
        """
        if change_mode == "cursor_moved":
            self._draw_cursor_text()

        elif change_mode == "range_changed":
            self._draw_cursor_and_range_text()

        elif change_mode == "plot_region_changed":
            self._calculate_bucket_data()
            self._draw_all_text()
            self._valid_bucket_range = \
                             self._histogram_control.valid_bucket_range()

        elif change_mode == "preferences_changed":
            self._draw_all_text()

        elif change_mode == "fit_range":
            self._histogram_control.fit_range()
            self._calculate_bucket_data()
            self._draw_all_text()
            self._valid_bucket_range = \
                             self._histogram_control.valid_bucket_range()

        elif change_mode == "filter_changed":
            self._hash_counts = self._data_manager.calculate_hash_counts()
            self._calculate_bucket_data()
            self._draw_all_text()

        elif change_mode == "data_changed":
            self._hash_counts = self._data_manager.calculate_hash_counts()
            self._calculate_bucket_data()
            self._draw_all_text()
            self._valid_bucket_range = \
                             self._histogram_control.valid_bucket_range()

        else:
            raise RuntimeError("program error in mode '%s'" % change_mode)

        # draw the histogram graph
        self._draw_clear()
        self._draw_range_selection()
        self._draw_x_axis()
        self._draw_buckets()
        self._draw_cursor_marker()

    def _draw_cursor_text(self):
        # just draw cursor text

        # cursor offset
        if self._histogram_control.is_valid_cursor or \
                                      self._histogram_control.is_valid_range:
            # cursor byte offset text
            self._c.itemconfigure(self._cursor_offset_id, text=offset_string(
                                     self._histogram_control.bound_offset(
                                     self._histogram_control.cursor_offset),
                                  self._preferences.offset_format,
                                  self._data_manager.sector_size))

        else:
            # clear
            self._c.itemconfigure(self._cursor_offset_id, text="")

        # cursor bucket count
        if self._histogram_control.is_valid_cursor and \
                              self._histogram_control.offset_is_on_bucket(
                              self._histogram_control.cursor_offset):
            # bucket count at cursor
            self._bucket_count_label["text"] = \
                          "Bar matches: %s, h=%s, i=%s" % (
                             self._source_buckets[
                             self._histogram_control.offset_to_bucket(
                                      self._histogram_control.cursor_offset)],
                             self._highlighted_source_buckets[
                             self._histogram_control.offset_to_bucket(
                                      self._histogram_control.cursor_offset)],
                             self._ignored_source_buckets[
                             self._histogram_control.offset_to_bucket(
                                      self._histogram_control.cursor_offset)])
        else:
            # clear
            self._bucket_count_label['text'] = "Bar matches: NA"

    def _draw_cursor_and_range_text(self):
        self._draw_cursor_text()
        # range selection text
        if self._histogram_control.is_valid_range:
            self._range_selection_label["text"] = \
                           "Range: %s \u2014 %s  (%s)" % (
                           # start_offset
                           offset_string(self._histogram_control.bound_offset(
                                         self._histogram_control.range_start),
                                         self._preferences.offset_format,
                                         self._data_manager.sector_size),
                           # stop_offset
                           offset_string(self._histogram_control.bound_offset(
                                         self._histogram_control.range_stop-1),
                                         self._preferences.offset_format,
                                         self._data_manager.sector_size),
                           # range
                           size_string(self._histogram_control.bound_offset(
                                       self._histogram_control.range_stop) -
                                       self._histogram_control.bound_offset(
                                       self._histogram_control.range_start)))
        else:
            self._range_selection_label["text"] = "Range: NA"

    def _draw_all_text(self):
        # draw all histogram annotations
        self._draw_cursor_text()
        self._draw_cursor_and_range_text()

        # bar width
        if self._histogram_control.bytes_per_bucket == 0:
            self._bucket_width_label["text"] = "Bar width: NA"
        else:
            self._bucket_width_label["text"] = "Bar width: %s" % \
                    offset_string(self._histogram_control.bytes_per_bucket,
                                  self._preferences.offset_format,
                                  self._data_manager.sector_size)

        # histogram start and stop text
        self._c.itemconfigure(self._start_offset_id, text=offset_string(
                  self._histogram_control.bound_offset(
                                  self._histogram_control.start_offset),
                                  self._preferences.offset_format,
                                  self._data_manager.sector_size))
        stop_offset = self._histogram_control.start_offset + (
                               self._histogram_control.bytes_per_bucket *
                               self._histogram_control.num_buckets) - 1
        self._c.itemconfigure(self._stop_offset_id, text=offset_string(
                  self._histogram_control.bound_offset(stop_offset),
                                  self._preferences.offset_format,
                                  self._data_manager.sector_size))

        # Y scale marker text
        self._c.itemconfigure(self._marker1_id, text=int_string(
                                                           self._y_scale))
        self._c.itemconfigure(self._marker2_id, text=int_string(
                                                           self._y_scale*10))
        self._c.itemconfigure(self._marker3_id, text=int_string(
                                                           self._y_scale*100))

    # clear histogram graph
    def _draw_clear(self):

        # clear any previous content
        self._photo_image.put("white",
                          to=(0,0,self._histogram_control.histogram_bar_width,
                                    histogram_constants.HISTOGRAM_BAR_HEIGHT))

    # draw black x axis across bottom
    def _draw_x_axis(self):
        self._photo_image.put(colors.X_AXIS,
                         to=(0, histogram_constants.HISTOGRAM_BAR_HEIGHT,
                         self._histogram_control.histogram_bar_width,
                         histogram_constants.HISTOGRAM_BAR_HEIGHT-1))

    # draw the range selection
    def _draw_range_selection(self):
        if self._histogram_control.is_valid_range:
            num_buckets = self._histogram_control.num_buckets

            # get bucket 1 value
            b1 = self._histogram_control.offset_to_bucket(
                                           self._histogram_control.range_start)
            if b1 < 0: b1 = 0
            if b1 > num_buckets: b1 = num_buckets
            x1 = b1 * histogram_constants.BUCKET_WIDTH

            # get bucket b2 value
            b2 = self._histogram_control.offset_to_bucket(
                                           self._histogram_control.range_stop)
            if b2 < 0: b2 = 0
            if b2 > num_buckets: b2 = num_buckets
            x2 = b2 * histogram_constants.BUCKET_WIDTH

            # keep range from becoming too narrow to plot
            if x2 == x1: x2 += 1

            # fill the range with the range selection color
            self._photo_image.put(colors.RANGE,
                    to=(x1, 0, x2, histogram_constants.HISTOGRAM_BAR_HEIGHT))

    # draw all the buckets
    def _draw_buckets(self):
        # skip empty initial-state data
        if self._histogram_control.bytes_per_bucket == -1:
            return

        # valid bucket boundaries map inside the image
        leftmost_bucket, rightmost_bucket = self._valid_bucket_range

        # draw the buckets
        for bucket in range(self._histogram_control.num_buckets):

            # bucket view depends on whether byte offset is in range
            if bucket >= leftmost_bucket and bucket <= rightmost_bucket:
                self._draw_bucket(bucket)
            else:
                self._draw_gray_bucket(bucket)

    """Calculate clipped bar height in pixels, using count, Y scale,
      and bucket height multiplier."""
    def _bar_height(self, count):
        h = int(count * histogram_constants.BUCKET_HEIGHT_MULTIPLIER //
                                                self._y_scale)

        # make small value visible
        if h == 0 and count > 0:
            h = 1

        # clip to keep in range
        if h > int(histogram_constants.HISTOGRAM_BAR_HEIGHT):
            h = int(histogram_constants.HISTOGRAM_BAR_HEIGHT)

        return h

    # draw one bar for one bucket
    def _draw_bar(self, color, count, i):

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * histogram_constants.BUCKET_WIDTH)
        y = self._bar_height(count)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             histogram_constants.HISTOGRAM_BAR_HEIGHT,
             x+histogram_constants.BUCKET_WIDTH,
             histogram_constants.HISTOGRAM_BAR_HEIGHT - y))

    # draw one tick mark for one bucket, see draw_bar
    def _draw_tick(self, color, count, i):

        # do not plot bars when count==0
        if not count:
            return

        # get coordinates
        x=(i * histogram_constants.BUCKET_WIDTH)
        y = self._bar_height(count)

        # plot rectangle
        self._photo_image.put(color, to=(
             x,
             histogram_constants.HISTOGRAM_BAR_HEIGHT - y + 1,
             x+histogram_constants.BUCKET_WIDTH,
             histogram_constants.HISTOGRAM_BAR_HEIGHT - y))

    # draw all bars for one bucket
    def _draw_bucket(self, i):

        # all sources with ignored sources removed: light blue bar
        self._draw_bar(colors.ALL_LIGHTER,
                    self._source_buckets[i] -
                    self._ignored_source_buckets[i], i)

        # all sources: light blue tick
        self._draw_tick(colors.ALL_LIGHTER,
                    self._source_buckets[i], i)

        # highlighted matches: light green bar
        self._draw_bar(colors.HIGHLIGHTED_LIGHTER,
                    self._highlighted_source_buckets[i], i)

    # draw one gray bucket for out-of-range data
    def _draw_gray_bucket(self, i):
        # x pixel coordinate
        x=(i * histogram_constants.BUCKET_WIDTH)

        # out of range so fill bucket area gray
        self._photo_image.put("gray",
                                to=(x, 0, x+histogram_constants.BUCKET_WIDTH,
                                   histogram_constants.HISTOGRAM_BAR_HEIGHT))

    # draw the cursor marker
    def _draw_cursor_marker(self):
        if self._histogram_control.is_valid_cursor:
            x = self._histogram_control.offset_to_bucket(
                                   self._histogram_control.cursor_offset) * \
                                             histogram_constants.BUCKET_WIDTH
            # zz
            if x < 0:
                x = 0
            self._photo_image.put("red", to=(x, 0, x+1,
                                   histogram_constants.HISTOGRAM_BAR_HEIGHT))

