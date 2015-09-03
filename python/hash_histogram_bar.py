import tkinter 
from forensic_path import offset_string

class HashHistogramBar():
    """Renders the histogram bar widget based on data, filter values, and zoom.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and move behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _byte_offset_selection_trace_var(IntVar): Setting this alerts
        listeners to the new selection.
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
    _cursor_offset = -1 # so it won't initially show

    # selection byte offset
    _is_valid_selection = False
    _selection_offset = -1 # so it won't initially show

    # mouse button 1 state
    _mouse_b1_pressed = False
    _mouse_b1_dragged = False
    _mouse_b1_down_x = None
    _mouse_b1_down_start_offset = None

    def __init__(self, master, identified_data, filters,
                 byte_offset_selection_trace_var):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          byte_offset_selection_trace_var(tkinter Var): Variable to
            communicate selection change.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._byte_offset_selection_trace_var = byte_offset_selection_trace_var

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
        f.pack(side=tkinter.TOP)
        tkinter.Label(f,text="   ",background="#000066").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="All matches      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#660000").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="No filtered matches      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#004400").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered matches only").pack(side=tkinter.LEFT)

        # add the byte offset label
        self._byte_offset_label = tkinter.Label(self.frame)
        self._byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected byte offset label
        self._selected_byte_offset_label = tkinter.Label(self.frame)
        self._selected_byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the histogram bar PhotoImage
        l = tkinter.Label(self.frame, image=self._photo_image,
                          relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)

        # add the frame for the leftmost and rightmost offset values
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP, fill=tkinter.X)
        self._start_offset_label = tkinter.Label(f)
        self._start_offset_label.pack(side=tkinter.LEFT)
        self._stop_offset_label = tkinter.Label(f)
        self._stop_offset_label.pack(side=tkinter.LEFT,
                                     expand=True, anchor=tkinter.E)

        # bind mouse motion events
        l.bind('<Any-Motion>', self._handle_mouse_move)
        l.bind('<Button-1>', self._handle_b1_mouse_press)
        l.bind('<ButtonRelease-1>', self._handle_b1_mouse_release)
        l.bind('<Enter>', self._handle_enter_window)
        l.bind('<Leave>', self._handle_leave_window)

        # bind mouse wheel events
        # https://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        l.bind("<MouseWheel>", self._handle_mouse_wheel)
        # with Linux OS
        l.bind("<Button-4>", self._handle_mouse_wheel)
        l.bind("<Button-5>", self._handle_mouse_wheel)

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        self._set_initial_state()
        self._set_identified_data()

    # this function is registered to and called by Filters
    def _handle_filter_change(self, *args):
        self._set_identified_data()

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):
        self._set_initial_state()

    def _set_initial_state(self):
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

    def _set_identified_data(self):
        # calculate this view
        self._calculate_hash_counts()
        self._calculate_bucket_data()

        # draw this view
        self._draw()

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
        self._draw_buckets()
        self._draw_marker_lines()

    def _draw_text(self):
 
        # put in the offset start and stop text
        self._start_offset_label["text"] = offset_string(self._start_offset)
        stop_offset = int(self._start_offset +
                          self._bytes_per_pixel * self.HISTOGRAM_BAR_WIDTH)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # put in the cursor byte offset text
        if self._is_valid_cursor:
            self._byte_offset_label["text"] = "Byte offset: " \
                               + offset_string(self._cursor_offset)
        else:
            # clear
            self._byte_offset_label['text'] = "Byte offset: Not selected"

        # put in the selection byte offset text
        if self._is_valid_selection:
            self._selected_byte_offset_label["text"] = \
                               "Byte offset selection: " \
                               + offset_string(self._selection_offset)
        else:
            # clear
            self._selected_byte_offset_label['text'] = \
                               "Byte offset selection: Not selected"

    # draw all the buckets
    def _draw_buckets(self):

        # clear any previous content
        self._photo_image.put("white", to=(0,0,self.HISTOGRAM_BAR_WIDTH,
                                               self.HISTOGRAM_BAR_HEIGHT))

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

        # draw horizontal separator lines between the three bucket groups
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

        # cursor marker
        if self._is_valid_cursor:
            x = self._offset_to_pixel(self._cursor_offset)
            if x >= 0 and x < self.HISTOGRAM_BAR_WIDTH:
                self._photo_image.put("red",
                                      to=(x, 0, x+1, self.HISTOGRAM_BAR_HEIGHT))

        # selection marker
        if self._is_valid_selection:
            x = self._offset_to_pixel(self._selection_offset)
            if x >= 0 and x < self.HISTOGRAM_BAR_WIDTH:
                self._photo_image.put("red3",
                                      to=(x, 0, x+1, self.HISTOGRAM_BAR_HEIGHT))

    # convert mouse coordinate to byte offset
    def _mouse_to_offset(self, e):
        # get x from mouse
        byte_offset = int(self._start_offset + self._bytes_per_pixel * (e.x))

        # return offset rounded down
        return byte_offset - byte_offset % self._sector_size

    def _in_image_range(self, offset):
        return offset >= 0 and offset < self._image_size

    # convert byte offset to pixel
    def _offset_to_pixel(self, byte_offset):
        # get x from mouse
        pixel = int((byte_offset - self._start_offset) / self._bytes_per_pixel)
        return pixel

    def _handle_enter_window(self, e):
        self._handle_mouse_move(e)

    def _handle_leave_window(self, e):
        self._is_valid_cursor = False
        self._draw()

    def _handle_mouse_move(self, e):

        # maybe pan
        if self._mouse_b1_pressed:

            # pan
            self._mouse_b1_dragged = True
            self._pan(e.x)

            # recalculate bucket data
            self._calculate_bucket_data()

        # always move cursor
        self._set_cursor(e)
        self._draw()

    def _handle_b1_mouse_press(self, e):
        self._mouse_b1_dragged = False
        self._mouse_b1_pressed = True
        self._mouse_b1_down_x = e.x
        self._mouse_b1_down_start_offset = self._start_offset

    def _handle_b1_mouse_release(self, e):
        self._mouse_b1_pressed = False

        # drag, so no action
        if self._mouse_b1_dragged:
            return

        # mouse click
        self._set_selection(e)
        self._draw()
        if self._is_valid_selection:
            self._byte_offset_selection_trace_var.set(self._selection_offset)
        else:
            self._byte_offset_selection_trace_var.set(-1)

    def _handle_mouse_wheel(self, e):
        # drag, so no action
        if self._mouse_b1_pressed:
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

    def _set_selection(self, e):
        self._selection_offset = self._mouse_to_offset(e)
        self._is_valid_selection = self._in_image_range(self._cursor_offset)

    def _pan(self, x):
            self._start_offset = int(self._mouse_b1_down_start_offset - 
                     self._bytes_per_pixel * (x - self._mouse_b1_down_x))
            self._start_offset -= self._start_offset % self._sector_size

    def _zoom(self, ratio):
        """Recalculate _start_offset and _bytes_per_bucket."""

        # get the zoom origin pixel
        zoom_origin_pixel = self._offset_to_pixel(self._cursor_offset)

        # calculate the bytes per pixel
        self._bytes_per_pixel = self._bytes_per_pixel * (ratio)

        # do not let bytes per pixel get too small
        if self._bytes_per_pixel * self.BUCKET_WIDTH < self._sector_size:
            self._bytes_per_pixel = self._sector_size / self.BUCKET_WIDTH

        # calculate the new start offset
        self._start_offset = int(self._cursor_offset -
                                 self._bytes_per_pixel * zoom_origin_pixel)
        self._start_offset -= self._start_offset % self._sector_size

