import tkinter 
from forensic_path import offset_string

class HashZoomBar():
    """Renders the zoom bar widget based on data, settings, and zoom.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and move behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _byte_offset_selection_trace_var(IntVar): Setting this alerts
        listeners to the new selection.
    """

    # number of buckets across the zoom bar
    MAX_BUCKETS = 200

    # pixels per bucket
    BUCKET_WIDTH = 3

    # maximum histogram height
    MAX_HISTOGRAM_HEIGHT = 20

    # zoom bar size in pixels
    ZOOM_BAR_WIDTH = MAX_BUCKETS * BUCKET_WIDTH
    ZOOM_BAR_HEIGHT = (20 + MAX_HISTOGRAM_HEIGHT) * 2

    # light to dark blue
    _colors = ["#ffffff",
               "#99ffff","#66ffff","#33ffff",
               "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
               "#0000ff","#0000cc","#000099","#000066"]
    # white through blue to black, 0 is white, not used, and 15 is black
    #_colors = ["#ffffff","#ccffff","#99ffff","#66ffff","#33ffff",
    #           "#00ffff","#00ccff","#0099ff","#0066ff","#0033ff",
    #           "#0000ff","#0000cc","#000099","#000066","#000033",
    #           "#000000"]


    # position variables
    _start_offset = 0
    _bytes_per_bucket = 0

    # cursor bucket index or -1 for none
    _cursor_index = -1

    # selection bucket index or -1 for none
    _selection_index = -1

    def __init__(self, master, identified_data, data_preferences,
                 byte_offset_selection_trace_var):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          selection_data(SelectionData): Various selected data.
          trace_vars(list of Var): Variables to communicate selection change.
        """

        # data variables
        self._identified_data = identified_data
        self._data_preferences = data_preferences
        self._byte_offset_selection_trace_var = byte_offset_selection_trace_var

        # data constants
        self.IMAGE_SIZE = self._identified_data.image_size
        self.SECTOR_SIZE = self._identified_data.sector_size

        # number of buckets, usually MAX_BUCKETS
        num_sectors = (self.IMAGE_SIZE +
                       self.SECTOR_SIZE - 1) // \
                       self.SECTOR_SIZE
        if num_sectors < self.MAX_BUCKETS:
            # for small dataset, NUM_BUCKETS can be less than MAX_BUCKETS
            self.NUM_BUCKETS = num_sectors
        else:
            self.NUM_BUCKETS = self.MAX_BUCKETS

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

        # add the byte offset label
        self._byte_offset_label = tkinter.Label(self.frame,
                                    text="Byte offset: Not selected")
        self._byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected byte offset label
        self._selected_byte_offset_label = tkinter.Label(self.frame,
                                   text="Selected byte offset: Not selected")
        self._selected_byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the zoom bar PhotoImage
        l = tkinter.Label(self.frame, image=self._photo_image,
                          relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)

        # add the frame for the leftmost and rightmost offset values
        f = tkinter.Frame(self.frame)
        f.pack(side=tkinter.TOP, fill=tkinter.X)
        self._start_offset_label = tkinter.Label(f, text="Not selected")
        self._start_offset_label.pack(side=tkinter.LEFT)
        self._stop_offset_label = tkinter.Label(f, text="Not selected")
        self._stop_offset_label.pack(side=tkinter.LEFT,
                                     expand=True, anchor=tkinter.E)

        # bind events
        l.bind('<Any-Motion>', self._handle_mouse_move)
        l.bind('<Button-1>', self._handle_mouse_click)
        l.bind('<Enter>', self._handle_mouse_move)
        l.bind('<Leave>', self._handle_leave_window)

        # initial zoomed-out variables
        self._start_offset = 0
        self._bytes_per_bucket = self._identified_data.image_size / \
                                                           self.NUM_BUCKETS

        self._draw()

    # draw
    def _draw(self):
        """Draw the offset values and the zoom bar."""

        # define the number of histogram buckets to draw
        num_buckets = self.NUM_BUCKETS
        num_sectors = (self.IMAGE_SIZE +
                       self.SECTOR_SIZE - 1) // \
                       self.SECTOR_SIZE
        if num_buckets > num_sectors:
            num_buckets = num_sectors
 
        # create the bucket data
        self._data = [0] * (num_buckets)
        self._filtered_data = [0] * (num_buckets)

        # calculate the histogram
        for key in self._identified_data.forensic_paths:
            offset = int(key)
            bucket = int((offset - self._start_offset) / self._bytes_per_bucket)
            if (bucket >= 0 and bucket < self.NUM_BUCKETS):
                self._data[bucket] += 1

        # put in the offset range text
        stop_offset = int(self._start_offset +
                          self._bytes_per_bucket * num_buckets)
        self._start_offset_label["text"] = offset_string(self._start_offset)
        self._stop_offset_label["text"] = offset_string(stop_offset)

        # clear the PhotoImage
        self._photo_image.put("gray", to=(0, 0, self.ZOOM_BAR_WIDTH,
                                                self.ZOOM_BAR_HEIGHT))

        # draw the buckets
        for i in range(self.NUM_BUCKETS):
            self._draw_bucket(i)

    # convert mouse coordinate to bucket or -1 if out of image range
    def _mouse_to_bucket(self, e):
        # get x from mouse
        bucket = int((e.x - 2) // self.BUCKET_WIDTH)
        if bucket < 0: bucket=0
        if bucket >= self.NUM_BUCKETS: bucket = -1

        return bucket

    # convert bucket to byte offset or -1 if out of image range
    def _bucket_to_byte_offset(self, bucket):
        if bucket == -1: return -1
        return self._start_offset + int(bucket * self._bytes_per_bucket / \
                                  self.SECTOR_SIZE) * self.SECTOR_SIZE

    def _handle_mouse_move(self, e):
        bucket = self._mouse_to_bucket(e)
        self._set_cursor(bucket)

    def _handle_leave_window(self, e):
        self._set_cursor(-1)

    def _handle_mouse_click(self, e):
        bucket = self._mouse_to_bucket(e)
        self._set_selection(bucket)


    # set a bucket as being hovered over by the mouse
    def _set_cursor(self, bucket):

        # clear old cursor bucket
        if self._cursor_index != -1:
            old_index = self._cursor_index
            self._cursor_index = -1
            self._draw_bucket(old_index)

        # set new cursor index
        self._cursor_index = bucket

        # set views based on cursor index
        if bucket != -1:
            # draw new selection
            self._draw_bucket(bucket)

            # put in the byte offset text
            byte_offset = self._bucket_to_byte_offset(bucket)
            self._byte_offset_label["text"] = "Byte offset: " \
                               + offset_string(byte_offset)
        else:
            # clear to -1
            self._byte_offset_label['text'] = "Byte offset: Not selected"

    # select a cell being clicked on by the mouse
    def _set_selection(self, bucket):

        # clear old selection bucket
        if self._selection_index != -1:
            old_index = self._selection_index
            self._selection_index = -1
            self._draw_bucket(old_index)

        # set new selection index
        self._selection_index = bucket

        # set views and trace var based on selection index
        if bucket != -1:
            # draw new selection
            self._draw_bucket(bucket)

            # calculate the byte offset
            byte_offset = self._bucket_to_byte_offset(bucket)

            # put in the byte offset selection text
            self._selected_byte_offset_label['text'] = \
                        "Selected byte offset: " + offset_string(byte_offset)

            # set trace var
            self._byte_offset_selection_trace_var.set(byte_offset)

        else:
            # clear to -1
            self._byte_offset_selection_trace_var.set(-1)
            self.selected_byte_offset_label['text'] = \
                                     "Selected byte offset: Not selected"

    # draw bucket at index considering _cursor_index and _selection_index
    def _draw_bucket(self, bucket):
        # x pixel coordinate
        x=(bucket * self.BUCKET_WIDTH)

        # clear any previous content
        self._photo_image.put("white", to=(x,0,x+self.BUCKET_WIDTH,
                                                    self.ZOOM_BAR_HEIGHT))

        # draw any marker
        if bucket == self._cursor_index: marker_color = "red"
        elif bucket == self._selection_index: marker_color = "red3"
        else: marker_color = None
        if marker_color is not None:
            self._photo_image.put(marker_color, to=(x,0,x+self.BUCKET_WIDTH,
                                                    self.ZOOM_BAR_HEIGHT))

        # draw the bucket
        bucket_color = "#000066"
        y = self._data[bucket]
        if y > self.MAX_HISTOGRAM_HEIGHT:
            y = self.MAX_HISTOGRAM_HEIGHT
            self._photo_image.put(bucket_color,
                      to=(x,                   self.ZOOM_BAR_HEIGHT - y,
                          x+self.BUCKET_WIDTH, self.ZOOM_BAR_HEIGHT))

