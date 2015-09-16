import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection

class HashHistogramBar():
    """Renders the histogram bar widget based on data, filter values, and zoom.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and move behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _hash_counts(dict of <hash, (count, filter_count)>): count
        and calculated filter count for each hash.
    """
    # number of buckets across the histogram bar
    NUM_BUCKETS = 220

    # pixels per bucket
    BUCKET_WIDTH = 3

    # histogram bar size in pixels
    HISTOGRAM_BAR_WIDTH = NUM_BUCKETS * BUCKET_WIDTH
    HISTOGRAM_BAR_HEIGHT = 261 # make divisible by 3 so bar rows align

    # cursor byte offset
    _is_valid_cursor = False
    _cursor_offset = 0

    # histogram state
    _histogram_b1_pressed = False
    _histogram_b1_start_offset = 0
    _histogram_dragged = False

    # pan state
    _pan_down_x = None
    _pan_down_start_offset = None

    def __init__(self, master, identified_data, filters, offset_selection,
                                                         range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection
        self._range_selection = range_selection

        # the photo_image
        self._photo_image = tkinter.PhotoImage(width=self.HISTOGRAM_BAR_WIDTH,
                                               height=self.HISTOGRAM_BAR_HEIGHT)
        self._photo_image.put("gray", to=(0, 0, self.HISTOGRAM_BAR_WIDTH,
                                                self.HISTOGRAM_BAR_HEIGHT))

        # make the containing frame
        self.frame = tkinter.Frame(master)
        self.frame.pack()

        # add the title
        tkinter.Label(self.frame, text="Image Match Histogram").pack(
                                                       side=tkinter.TOP)

        # add the color legend
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP, pady=4)
        tkinter.Label(f,text="   ",background="#000066").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="All matches      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#660000").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="No filtered matches      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#004400").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered matches only").pack(side=tkinter.LEFT)

        # add the label containing the histogram bar PhotoImage
        l = tkinter.Label(self.frame, image=self._photo_image,
                          relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)

        # add the frame for offset values and button controls
        f = tkinter.Frame(self.frame, height=22+4, pady=4)
        f.pack(side=tkinter.TOP, fill=tkinter.X)

        # leftmost offset value
        self._start_offset_label = tkinter.Label(f)
        self._start_offset_label.place(relx=0.0, anchor=tkinter.NW)

        # button controls
        control_frame = tkinter.Frame(f)
        control_frame.place(relx=0.49, anchor=tkinter.N)
        
        # pan
        self._pan_icon = tkinter.PhotoImage(file=icon_path("pan"))
        pan_button = tkinter.Button(control_frame, image=self._pan_icon)
        pan_button.pack(side=tkinter.LEFT)
        pan_button.config(cursor="sb_h_double_arrow")
        Tooltip(pan_button, "Drag to pan")

        # bind pan control mouse events
        pan_button.bind('<Button-1>', self._handle_pan_press)
        pan_button.bind('<B1-Motion>', self._handle_pan_move)

        # zoom to fit image
        self._fit_image_icon = tkinter.PhotoImage(file=icon_path("fit_image"))
        fit_image_button = tkinter.Button(control_frame,
                                          image=self._fit_image_icon,
                                          command=self._handle_fit_image)
        fit_image_button.pack(side=tkinter.LEFT)
        Tooltip(fit_image_button, "Zoom to fit image")

        # zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(control_frame,
                                          image=self._fit_range_icon,
                                          command=self._handle_fit_range)
        self._fit_range_button.pack(side=tkinter.LEFT, padx=(8,0))
        Tooltip(self._fit_range_button, "Zoom to range")

        # filter sources in range
        self._filter_sources_in_range_icon = tkinter.PhotoImage(
                                  file=icon_path("filter_range"))
        self._filter_sources_in_range_button = tkinter.Button(control_frame,
                                  image=self._filter_sources_in_range_icon,
                                  command=self._handle_filter_sources_in_range)
        self._filter_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._filter_sources_in_range_button, "Filter sources in range")

        # filter all but sources in range
        self._filter_all_but_sources_in_range_icon = tkinter.PhotoImage(
                          file=icon_path("filter_all_but_range"))
        self._filter_all_but_sources_in_range_button = tkinter.Button(
                          control_frame,
                          image=self._filter_all_but_sources_in_range_icon,
                          command=self._handle_filter_all_but_sources_in_range)
        self._filter_all_but_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._filter_all_but_sources_in_range_button,
                          "Filter all but sources in range")

        # deselect range
        self._deselect_range_icon = tkinter.PhotoImage(
                                  file=icon_path("deselect_range"))
        self._deselect_range_button = tkinter.Button(control_frame,
                                  image=self._deselect_range_icon,
                                  command=self._handle_deselect_range)
        self._deselect_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._deselect_range_button, "Deselect range")

        # rightmost offset value
        self._stop_offset_label = tkinter.Label(f)
        self._stop_offset_label.place(relx=1.0, anchor=tkinter.NE)

        # bind histogram mouse motion events
        l.bind('<Any-Motion>', self._handle_histogram_motion)
        l.bind('<Button-1>', self._handle_histogram_b1_press)
        l.bind('<ButtonRelease-1>', self._handle_histogram_b1_release)
        l.bind('<Enter>', self._handle_histogram_enter)
        l.bind('<Leave>', self._handle_histogram_leave)

        # bind histogram mouse wheel events
        # https://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        l.bind("<MouseWheel>", self._handle_histogram_mouse_wheel)
        # with Linux OS
        l.bind("<Button-4>", self._handle_histogram_mouse_wheel)
        l.bind("<Button-5>", self._handle_histogram_mouse_wheel)

        # add the selection frame
        selection_frame = tkinter.Frame(self.frame)
        selection_frame.pack(side=tkinter.TOP, anchor="w")

        # add the status frame to the left of the selection frame
        status_frame = tkinter.Frame(selection_frame)
        status_frame.pack(side=tkinter.LEFT)

        # add the image byte offset label to status_frame
        self._image_offset_label = tkinter.Label(status_frame)
        self._image_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected image byte offset label
        self._selected_image_offset_label = tkinter.Label(status_frame)
        self._selected_image_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected image byte offset hash label
        self._selected_image_offset_hash_label = tkinter.Label(status_frame,
                                                       width=55, anchor="w")
        self._selected_image_offset_hash_label.pack(side=tkinter.TOP,
                                                               anchor="w")

        # add the hash filter frame to the right of the selection frame
        hash_filter_frame = tkinter.Frame(selection_frame)
        hash_filter_frame.pack(side=tkinter.LEFT)

        # add hash filter "Hash filter:" text to the hash filter frame
        tkinter.Label(hash_filter_frame, text="Hash filter:").pack(
                                                       side=tkinter.LEFT)

        # hash_filter_frame "Add Hash to Filter" button to the hash filter frame
        self._add_hash_icon = tkinter.PhotoImage(file=icon_path("add_hash"))
        self._add_hash_button = tkinter.Button(hash_filter_frame,
                                image=self._add_hash_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_add_hash_to_filter)
        self._add_hash_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(self._add_hash_button, "Filter the selected hash")

        # hash_filter_frame "Remove Hash from Filter" button
        self._remove_hash_icon = tkinter.PhotoImage(file=icon_path(
                                                              "remove_hash"))
        self._remove_hash_button = tkinter.Button(hash_filter_frame,
                                image=self._remove_hash_icon,
                                state=tkinter.DISABLED,
                                command=self._handle_remove_hash_from_filter)
        self._remove_hash_button.pack(side=tkinter.LEFT)
        Tooltip(self._remove_hash_button, "Stop filtering the selected hash")

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)
        filters.set_callback(self._handle_offset_selection_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

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

        # initial zoomed-out position variables
        self._start_offset = 0
        self._bytes_per_pixel = self._image_size / self.HISTOGRAM_BAR_WIDTH

        # bytes per pixel may be fractional but not less than one
        # sector per bucket
        if self._bytes_per_pixel * self.BUCKET_WIDTH < self._sector_size:
            self._bytes_per_pixel = self._sector_size / self.BUCKET_WIDTH

        # calculate this view
        self._calculate_hash_counts()
        self._calculate_bucket_data()

        # draw
        self._draw()

    # this function is registered to and called by OffsetSelection
    def _handle_offset_selection_change(self, *args):
        self._set_add_and_remove_button_states()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            self._fit_range_button.config(state=tkinter.NORMAL)
            self._filter_sources_in_range_button.config(state=tkinter.NORMAL)
            self._filter_all_but_sources_in_range_button.config(
                                                        state=tkinter.NORMAL)
            self._deselect_range_button.config(state=tkinter.NORMAL)
        else:
            self._fit_range_button.config(state=tkinter.DISABLED)
            self._filter_sources_in_range_button.config(state=tkinter.DISABLED)
            self._filter_all_but_sources_in_range_button.config(
                                                        state=tkinter.DISABLED)
            self._deselect_range_button.config(state=tkinter.DISABLED)

    def _set_add_and_remove_button_states(self):
        # disable both if there is no active selection
        if self._offset_selection.offset == -1:
            self._add_hash_button.config(state=tkinter.DISABLED)
            self._remove_hash_button.config(state=tkinter.DISABLED)
            return

        # reference to selected hash
        selected_hash = self._offset_selection.block_hash

        # set enabled state of the add hash button
        if selected_hash not in self._filters.filtered_hashes and \
                           selected_hash in self._identified_data.hashes:
            self._add_hash_button.config(state=tkinter.NORMAL)
        else:
            self._add_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the remove hash button
        if selected_hash in self._filters.filtered_hashes:
            self._remove_hash_button.config(state=tkinter.NORMAL)
        else:
            self._remove_hash_button.config(state=tkinter.DISABLED)

    # button changes filter
    def _handle_add_hash_to_filter(self):
        self._filters.filtered_hashes.add(self._offset_selection.block_hash)
        self._filters.fire_change()

    # button changes filter
    def _handle_remove_hash_from_filter(self):
        self._filters.filtered_hashes.remove(self._offset_selection.block_hash)
        self._filters.fire_change()

    def _calculate_hash_counts(self):

        # optimization: make local references to filter variables
        max_hashes = self._filters.max_hashes
        filter_flagged_blocks = self._filters.filter_flagged_blocks
        filtered_sources = self._filters.filtered_sources
        filtered_hashes = self._filters.filtered_hashes

        # calculate _hash_counts based on identified data
        # _hash_counts is dict<hash, (count, filter_count)>
        self._hash_counts = dict()
        for block_hash, sources in self._identified_data.hashes.items():
            count = len(sources)
            filter_count = 0

            # determine filter_count

            # count exceeds max_hashes
            if max_hashes != 0 and count > max_hashes:
                filter_count = count

            # hash is filtered
            elif block_hash in filtered_hashes:
                filter_count = count

            # a source is flagged or a source itself is filtered
            else:
                for source in sources:
                    if filter_flagged_blocks and "label" in source:
                        # source has a label flag
                        filter_count += 1
                        continue
                    if source["source_id"] in filtered_sources:
                        # source is to be filtered
                        filter_count += 1
                        continue

            # set the count and filter_count for the hash
            self._hash_counts[block_hash] = (count, filter_count)

    def _calculate_bucket_data(self):
        """Buckets show hashes per bucket and sources per bucket.  Bucket
        types show all, filter removed, and filter only matches.
        """
        self._hash_buckets = [0] * (self.NUM_BUCKETS)
        self._source_buckets = [0] * (self.NUM_BUCKETS)
        self._filter_removed_hash_buckets = [0] * (self.NUM_BUCKETS)
        self._filter_removed_source_buckets = [0] * (self.NUM_BUCKETS)
        self._filter_only_hash_buckets = [0] * (self.NUM_BUCKETS)
        self._filter_only_source_buckets = [0] * (self.NUM_BUCKETS)

        # calculate the histogram
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            bucket = (offset - self._start_offset) / \
                (self._bytes_per_pixel * self.BUCKET_WIDTH)
            if bucket < 0 or bucket >= self.NUM_BUCKETS:
                # offset is out of range of buckets
                continue

            # get bucket number as int
            bucket = int(bucket)

            # set values for buckets
            count, filter_count = self._hash_counts[block_hash]

            # hash buckets
            self._hash_buckets[bucket] += 1
            self._source_buckets[bucket] += count

            # hashes with filter removed
            if count - filter_count > 0:
                self._filter_removed_hash_buckets[bucket] += 1
                self._filter_removed_source_buckets[bucket] += \
                                                     count - filter_count

            # hashes with filter
            if filter_count > 0:
                self._filter_only_hash_buckets[bucket] += 1
                self._filter_only_source_buckets[bucket] += filter_count

    # redraw everything
    def _draw(self):
        self._draw_text()
        self._draw_clear()
        self._draw_range_selection()
        self._draw_buckets()
        self._draw_separator_lines()
        self._draw_marker_lines()

    def _draw_text(self):
 
        # put in the offset start and stop text
        self._start_offset_label["text"] = offset_string(self._start_offset)
        stop_offset = int(self._start_offset +
                          self._bytes_per_pixel * self.HISTOGRAM_BAR_WIDTH)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # put in the cursor byte offset text
        if self._is_valid_cursor:
            self._image_offset_label["text"] = "Image offset: " \
                               + offset_string(self._cursor_offset)
        else:
            # clear
            self._image_offset_label['text'] = "Image offset: Not selected"

        # put in the sector selection byte offset text
        if self._offset_selection.offset == -1:
            # clear
            self._selected_image_offset_label['text'] = \
                               "Selected image offset: Not selected"
            self._selected_image_offset_hash_label['text'] = \
                               "Selected block hash: Not selected"

        else:
            self._selected_image_offset_label["text"] = \
                              "Selected image offset: %s" % offset_string(
                                          self._offset_selection.offset)
            self._selected_image_offset_hash_label["text"] = \
                 "Selected block hash: %s" % self._offset_selection.block_hash

    # clear everything
    def _draw_clear(self):

        # clear any previous content
        self._photo_image.put("white", to=(0,0,self.HISTOGRAM_BAR_WIDTH,
                                               self.HISTOGRAM_BAR_HEIGHT))

    # draw the range selection
    def _draw_range_selection(self):
        if self._range_selection.is_selected:
            # get pixel x1 value
            x1 = self._offset_to_pixel(self._range_selection.start_offset)
            if x1 < 0: x1 = 0
            if x1 > self.HISTOGRAM_BAR_WIDTH: x1 = self.HISTOGRAM_BAR_WIDTH

            # get pixel x2 value
            x2 = self._offset_to_pixel(self._range_selection.stop_offset)
            if x2 < 0: x2 = 0
            if x2 > self.HISTOGRAM_BAR_WIDTH: x2 = self.HISTOGRAM_BAR_WIDTH

            # keep range from becoming too narrow to plot
            if x2 == x1: x2 += 1

            # fill the range with the range selection color
            self._photo_image.put("#ccffff",
                                 to=(x1, 0, x2, self.HISTOGRAM_BAR_HEIGHT))

    # draw all the buckets
    def _draw_buckets(self):

        # valid bucket boundaries map inside the image
        leftmost_bucket = max(int((0 - self._start_offset) /
                          (self._bytes_per_pixel * self.BUCKET_WIDTH)),
                          0)
        rightmost_bucket = min(int((self._image_size - self._start_offset) /
                          (self._bytes_per_pixel * self.BUCKET_WIDTH)),
                          self.NUM_BUCKETS)

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

    # draw one bar for one bucket
    def _draw_bar(self, color, count, i, j):
        # i is bucket number
        # j is bar row number, either 2, 1, or 0
        # x is pixel coordinate
        x=(i * self.BUCKET_WIDTH)
        y0 = int(self.HISTOGRAM_BAR_HEIGHT / 3 * j)
        y1 = int(self.BUCKET_WIDTH * count)
        if y1 > int(self.HISTOGRAM_BAR_HEIGHT / 3):
            y1 = int(self.HISTOGRAM_BAR_HEIGHT / 3)

        self._photo_image.put(color, to=(
             x,
             self.HISTOGRAM_BAR_HEIGHT - y0,
             x+self.BUCKET_WIDTH,
             self.HISTOGRAM_BAR_HEIGHT - (y0 + y1)))

    # draw all bars for one bucket
    def _draw_bucket(self, i):

        # draw bars
        self._draw_bar("#3399ff", self._source_buckets[i], i, 2)
        self._draw_bar("#000066", self._hash_buckets[i], i, 2)
        self._draw_bar("#ff5050", self._filter_removed_source_buckets[i], i, 1)
        self._draw_bar("#660000", self._filter_removed_hash_buckets[i], i, 1)
        self._draw_bar("#33cc33", self._filter_only_source_buckets[i], i, 0)
        self._draw_bar("#004400", self._filter_only_hash_buckets[i], i, 0)

    # draw one gray bucket for out-of-range data
    def _draw_gray_bucket(self, i):
        # x pixel coordinate
        x=(i * self.BUCKET_WIDTH)

        # out of range so fill bucket area gray
        self._photo_image.put("gray", to=(x, 0, x+self.BUCKET_WIDTH,
                                                  self.HISTOGRAM_BAR_HEIGHT))


    # draw the selection and cursor markers
    def _draw_marker_lines(self):

        # cursor marker when valid and not selecting a range
        if self._is_valid_cursor and not self._histogram_dragged:
            x = self._offset_to_pixel(self._cursor_offset)
            if x >= 0 and x < self.HISTOGRAM_BAR_WIDTH:
                self._photo_image.put("red",
                                      to=(x, 0, x+1, self.HISTOGRAM_BAR_HEIGHT))

        # sector selection marker
        if self._offset_selection.offset != -1:
            x = self._offset_to_pixel(self._offset_selection.offset)
            if x >= 0 and x < self.HISTOGRAM_BAR_WIDTH:
                self._photo_image.put("red3",
                                      to=(x, 0, x+1, self.HISTOGRAM_BAR_HEIGHT))

    # convert mouse coordinate to byte offset
    def _mouse_to_offset(self, e):
        # get x from mouse
        image_offset = int(self._start_offset + self._bytes_per_pixel * (e.x))

        # return offset rounded down to sector boundary
        return image_offset - image_offset % self._sector_size

    def _in_image_range(self, offset):
        return offset >= 0 and offset < self._image_size

    # convert byte offset to pixel
    def _offset_to_pixel(self, image_offset):
        # get x from mouse
        pixel = int((image_offset - self._start_offset) / self._bytes_per_pixel)
        return pixel

    def _handle_pan_press(self, e):
        self._pan_down_x = e.x
        self._pan_down_start_offset = self._start_offset

    def _handle_pan_move(self, e):
        # pan
        new_start_offset = int(self._pan_down_start_offset - 
                 self._bytes_per_pixel * (e.x - self._pan_down_x))
        new_start_offset -= new_start_offset % self._sector_size

        if not self._out_of_range(new_start_offset, self._bytes_per_pixel):
            # accept the pan
            self._start_offset = new_start_offset

            # recalculate bucket data
            self._calculate_bucket_data()
            self._draw()

    def _handle_histogram_enter(self, e):
        self._handle_histogram_motion(e)

    def _handle_histogram_leave(self, e):
        self._is_valid_cursor = False
        self._draw()

    def _handle_histogram_b1_press(self, e):
        self._histogram_b1_pressed = True
        self._histogram_b1_start_offset = self._mouse_to_offset(e)

    def _handle_histogram_motion(self, e):
        if self._histogram_b1_pressed:
            # mark as drag as opposed to click
            self._histogram_dragged = True

            # select range
            self._range_selection.set(self._histogram_b1_start_offset,
                                                  self._mouse_to_offset(e))

        # show mouse motion
        self._set_cursor(e)

        # draw
        self._draw()

    def _handle_histogram_b1_release(self, e):
        self._histogram_b1_pressed = False

        if self._histogram_dragged:
            # end b1 range selection motion
            self._histogram_dragged = False

        else:
            # select the clicked sector
            sector_offset = self._mouse_to_offset(e)
            if self._in_image_range(sector_offset):
                # sector is in image range
                self._offset_selection.set(self._identified_data.image_filename,
                                           sector_offset,
                                           self._identified_data.block_size)

            else:
                self._offset_selection.clear()

        # button up so show the cursor
        self._set_cursor(e)
        self._draw()

    def _handle_histogram_mouse_wheel(self, e):
        # drag, so no action
        if self._histogram_b1_pressed:
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
        self._cursor_offset = self._mouse_to_offset(e)
        self._is_valid_cursor = self._in_image_range(self._cursor_offset)

    def _zoom(self, ratio):
        """Recalculate _start_offset and _bytes_per_bucket."""

        # get the zoom origin pixel
        zoom_origin_pixel = self._offset_to_pixel(self._cursor_offset)

        # calculate the new bytes per pixel
        new_bytes_per_pixel = self._bytes_per_pixel * (ratio)

        # do not let bytes per pixel get too small
        if new_bytes_per_pixel * self.BUCKET_WIDTH < self._sector_size:
            new_bytes_per_pixel = self._sector_size / self.BUCKET_WIDTH

        # calculate the new start offset
        new_start_offset = int(self._cursor_offset -
                                 new_bytes_per_pixel * zoom_origin_pixel)
        new_start_offset -= new_start_offset % self._sector_size

        if not self._out_of_range(new_start_offset, new_bytes_per_pixel):
           self._start_offset = new_start_offset
           self._bytes_per_pixel = new_bytes_per_pixel

    def _out_of_range(self, start_offset, bytes_per_pixel):
        # media image is outside range of graph
        end_offset = start_offset + bytes_per_pixel * self.HISTOGRAM_BAR_WIDTH
        return start_offset > self._image_size or end_offset < 0

    def _handle_filter_sources_in_range(self):
        # clear existing filtered sources
        self._filters.filtered_sources.clear()

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and filter
        hashes = self._identified_data.hashes
        filtered_sources = self._filters.filtered_sources
        
        # filter sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so filter its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # filter each source associated with this hash
                for source in sources:
                    filtered_sources.add(source["source_id"])

        # fire filter change
        self._filters.fire_change()

    def _handle_filter_all_but_sources_in_range(self):
        # start by filtering all sources
        for source_id, _ in self._identified_data.source_details.items():
            self._filters.filtered_sources.add(source_id)

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and filter
        hashes = self._identified_data.hashes
        filtered_sources = self._filters.filtered_sources
        
        # unfilter sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so filter its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # unfilter each source associated with this hash
                for source in sources:
                    filtered_sources.discard(source["source_id"])

        # fire filter change
        self._filters.fire_change()

    def _handle_fit_range(self):
        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        new_bytes_per_pixel = (stop_byte - start_byte) / \
                              self.HISTOGRAM_BAR_WIDTH

        # do not let bytes per pixel get too small
        if new_bytes_per_pixel * self.BUCKET_WIDTH < self._sector_size:
            new_bytes_per_pixel = self._sector_size / self.BUCKET_WIDTH

        # calculate the new start offset
        new_start_offset = start_byte - start_byte % self._sector_size

        self._start_offset = new_start_offset
        self._bytes_per_pixel = new_bytes_per_pixel

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def _handle_fit_image(self):
        # initial zoomed-out position variables
        self._start_offset = 0
        self._bytes_per_pixel = self._image_size / self.HISTOGRAM_BAR_WIDTH

        # bytes per pixel may be fractional but not less than one
        # sector per bucket
        if self._bytes_per_pixel * self.BUCKET_WIDTH < self._sector_size:
            self._bytes_per_pixel = self._sector_size / self.BUCKET_WIDTH

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def _handle_deselect_range(self):
        # deselect range
        self._range_selection.clear()

        # redraw
        self._draw()

