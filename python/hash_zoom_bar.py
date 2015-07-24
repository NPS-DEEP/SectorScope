import tkinter 
from forensic_path import offset_string

class HashZoomBar():
    """Renders the zoom bar widget based on data, filter values, and zoom.

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

    # number of buckets across the zoom bar
    NUM_BUCKETS = 224

    # pixels per bucket
    BUCKET_WIDTH = 3

    # zoom bar size in pixels
    ZOOM_BAR_WIDTH = NUM_BUCKETS * BUCKET_WIDTH
    ZOOM_BAR_HEIGHT = 261 # make divisible by 3 for 3 even bar rows

    # cursor byte offset
    _is_valid_cursor = False
    _cursor_offset = -1 # so it won't initially show

    # selection byte offset
    _is_valid_selection = False
    _selection_offset = -1 # so it won't initially show

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

        # data constants
        self.IMAGE_SIZE = self._identified_data.image_size
        self.SECTOR_SIZE = self._identified_data.sector_size

        # initial zoomed-out position variables
        self._start_offset = 0
        self._bytes_per_pixel = self.IMAGE_SIZE / self.ZOOM_BAR_WIDTH

        # bytes per pixel may be fractional but not less than one
        # sector per bucket
        if self._bytes_per_pixel * self.BUCKET_WIDTH < self.SECTOR_SIZE:
            self._bytes_per_pixel = self.SECTOR_SIZE / self.BUCKET_WIDTH

        # the photo_image
        self._photo_image = tkinter.PhotoImage(width=self.ZOOM_BAR_WIDTH,
                                               height=self.ZOOM_BAR_HEIGHT)
        self._photo_image.put("gray", to=(0, 0, self.ZOOM_BAR_WIDTH,
                                                self.ZOOM_BAR_HEIGHT))

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
        tkinter.Label(f,text="Filtered matches removed      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#004400").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered matches only").pack(side=tkinter.LEFT)

        # add the byte offset label
        self._byte_offset_label = tkinter.Label(self.frame)
        self._byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected byte offset label
        self._selected_byte_offset_label = tkinter.Label(self.frame)
        self._selected_byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the zoom bar PhotoImage
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
        l.bind('<Button-1>', self._handle_mouse_click)
        l.bind('<Enter>', self._handle_enter_window)
        l.bind('<Leave>', self._handle_leave_window)

        # bind mouse wheel events
        # https://www.daniweb.com/software-development/python/code/217059/using-the-mouse-wheel-with-tkinter-python
        # with Windows OS
        l.bind("<MouseWheel>", self._handle_mouse_wheel)
        # with Linux OS
        l.bind("<Button-4>", self._handle_mouse_wheel)
        l.bind("<Button-5>", self._handle_mouse_wheel)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        self._calculate_hash_counts()
        self._calculate_bucket_data()
        self._draw()

    # this function is registered to and called by Filters
    def _handle_filter_change(self, *args):
        self._calculate_hash_counts()
        self._calculate_bucket_data()
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

            self._hash_buckets[bucket] += 1
            self._source_buckets[bucket] += count
            if filter_count > 0:
                self._filter_removed_hash_buckets[bucket] += 1
                self._filter_removed_source_buckets[bucket] += filter_count
            else:
                self._filter_only_hash_buckets[bucket] += 1
                self._filter_only_source_buckets[bucket] += filter_count

    # redraw everything
    def _draw(self):
        self._draw_bar_text()
        self._draw_buckets()
        self._draw_marker_lines()

    def _draw_bar_text(self):
 
        # put in the offset start and stop text
        self._start_offset_label["text"] = offset_string(self._start_offset)
        stop_offset = int(self._start_offset +
                          self._bytes_per_pixel * self.ZOOM_BAR_WIDTH)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # put in the cursor byte offset text
        if self._is_valid_cursor:
            self._byte_offset_label["text"] = "Byte offset: " \
                               + offset_string(self._cursor_offset)
        else:
            # clear to -1
            self._byte_offset_label['text'] = "Byte offset: Not selected"

        # put in the selection byte offset text
        if self._is_valid_selection:
            self._selected_byte_offset_label["text"] = \
                               "Byte offset selection: " \
                               + offset_string(self._selection_offset)
        else:
            # clear to -1
            self._selected_byte_offset_label['text'] = \
                               "Byte offset selection: Not selected"

    # draw all the buckets
    def _draw_buckets(self):

        # clear any previous content
        self._photo_image.put("white", to=(0,0,self.ZOOM_BAR_WIDTH,
                                               self.ZOOM_BAR_HEIGHT))

        # draw the buckets
        for i in range(self.NUM_BUCKETS):

            # get byte offset for bucket
            byte_offset = int(self._start_offset + self._bytes_per_pixel * \
                          i * self.BUCKET_WIDTH)
            byte_offset -= byte_offset % self.SECTOR_SIZE

            # bucket view depends on whether byte offset is in range
            if byte_offset >= 0 and byte_offset < self.IMAGE_SIZE:
                self._draw_bucket(i)
            else:
                self._draw_gray_bucket(i)

    # draw one bar as part of a bucket
    def _draw_bar(self, color, count, i, j):
        # i is bucket number
        # j is bar row number, either 2, 1, or 0
        # x is pixel coordinate
        x=(i * self.BUCKET_WIDTH)
        y0 = int(self.ZOOM_BAR_HEIGHT / 3 * j)
        y1 = int(self.BUCKET_WIDTH * count)
        if y1 > int(self.ZOOM_BAR_HEIGHT / 3) - 1:
            y1 = int(self.ZOOM_BAR_HEIGHT / 3) - 1

        self._photo_image.put(color, to=(
             x,
             self.ZOOM_BAR_HEIGHT - y0,
             x+self.BUCKET_WIDTH,
             self.ZOOM_BAR_HEIGHT - (y0 + y1)))

    # draw one bucket
    def _draw_bucket(self, i):

        # draw bars
        self._draw_bar("#0000aa", self._source_buckets[i], i, 2)
        self._draw_bar("#000066", self._hash_buckets[i], i, 2)
        self._draw_bar("#aa0000", self._filter_only_source_buckets[i], i, 1)
        self._draw_bar("#660000", self._filter_only_hash_buckets[i], i, 1)
        self._draw_bar("#006600", self._filter_removed_source_buckets[i], i, 0)
        self._draw_bar("#004400", self._filter_removed_hash_buckets[i], i, 0)

    # draw one gray bucket for out-of-range data
    def _draw_gray_bucket(self, i):
        # x pixel coordinate
        x=(i * self.BUCKET_WIDTH)

        # out of range so fill bucket area gray
        self._photo_image.put("gray", to=(x, 0, x+self.BUCKET_WIDTH,
                                                    self.ZOOM_BAR_HEIGHT))


    # draw the selection and cursor markers
    def _draw_marker_lines(self):

        # cursor marker
        if self._is_valid_cursor:
            x = self._offset_to_pixel(self._cursor_offset)
            self._photo_image.put("red", to=(x, 0, x+1, self.ZOOM_BAR_HEIGHT))

        # selection marker
        if self._is_valid_selection:
            x = self._offset_to_pixel(self._selection_offset)
            if x >= 0 and x < self.ZOOM_BAR_WIDTH:
                self._photo_image.put("red3",
                                      to=(x, 0, x+1, self.ZOOM_BAR_HEIGHT))

    # convert mouse coordinate to byte offset
    def _mouse_to_offset(self, e):
        # get x from mouse
        byte_offset = int(self._start_offset + self._bytes_per_pixel * (e.x))

        # return offset rounded down
        return byte_offset - byte_offset % self.SECTOR_SIZE

    def _in_range(self, offset):
        return offset >= 0 and offset < self.IMAGE_SIZE

    # convert byte offset to pixel
    def _offset_to_pixel(self, byte_offset):
        # get x from mouse
        pixel = int((byte_offset - self._start_offset) / self._bytes_per_pixel)
        return pixel

    def _handle_enter_window(self, e):
        self._cursor_offset = self._mouse_to_offset(e)
        self._is_valid_cursor = self._in_range(self._cursor_offset)
        self._draw()

    def _handle_leave_window(self, e):
        self._is_valid_cursor = False
        self._draw()

    def _handle_mouse_move(self, e):
        self._cursor_offset = self._mouse_to_offset(e)
        self._is_valid_cursor = self._in_range(self._cursor_offset)
        self._draw()

    def _handle_mouse_click(self, e):
        self._selection_offset = self._mouse_to_offset(e)
        self._is_valid_selection = self._in_range(self._cursor_offset)
        self._draw()
        if self._is_valid_selection:
            self._byte_offset_selection_trace_var.set(self._selection_offset)
        else:
            self._byte_offset_selection_trace_var.set(-1)

    def _handle_mouse_wheel(self, e):
        if e.num == 4 or e.delta == 120:
            self._zoom_in()
        elif e.num == 5 or e.delta == -120:
            self._zoom_out()
        else:
            print("Unexpected _mouse_wheel")

    def _zoom_in(self):
        """Recalculate _start_offset and _bytes_per_bucket and then redraw."""
        before = self._bytes_per_pixel

        # get the zoom origin pixel
        zoom_origin_pixel = self._offset_to_pixel(self._cursor_offset)

        # calculate the bytes per pixel
        change = 0.33
        self._bytes_per_pixel = self._bytes_per_pixel * (1 - change)

        # do not let bytes per pixel get too small
        if self._bytes_per_pixel * self.BUCKET_WIDTH < self.SECTOR_SIZE:
            self._bytes_per_pixel = self.SECTOR_SIZE / self.BUCKET_WIDTH

        # calculate the new start offset based on offset at cursor
        self._start_offset = int(self._cursor_offset -
                                 self._bytes_per_pixel * zoom_origin_pixel)
        self._start_offset -= self._start_offset % self.SECTOR_SIZE

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

    def _zoom_out(self):
        """Recalculate _start_offset and _bytes_per_bucket and then redraw."""

        # get the zoom origin pixel
        zoom_origin_pixel = self._offset_to_pixel(self._cursor_offset)

        # calculate the bytes per pixel
        change = 0.33
        self._bytes_per_pixel = self._bytes_per_pixel / (1 - change)

        # calculate the new start offset based on offset at cursor
        self._start_offset = int(self._cursor_offset -
                                 self._bytes_per_pixel * zoom_origin_pixel)
        self._start_offset -= self._start_offset % self.SECTOR_SIZE

        # recalculate bucket data
        self._calculate_bucket_data()

        # redraw
        self._draw()

