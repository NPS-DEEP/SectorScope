import tkinter 
from forensic_path import offset_string

class HashZoomBar():
    """Renders the zoom bar widget based on data, settings, and zoom.

    See http://almende.github.io/chap-links-library/js/timeline/examples/example28_custom_controls.html
    for an example of zoom and move behavior.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): The image on which the plot is rendered.
      _image_overview_byte_offset_selection_trace_var(IntVar): Setting this
        alerts listeners to the new selection.
    """

    # number of buckets across the zoom bar
    NUM_BUCKETS = 200

    # pixels per bucket
    BUCKET_WIDTH = 3

    # maximum histogram height
    MAX_HISTOGRAM_HEIGHT = 20

    # zoom bar size in pixels
    ZOOM_BAR_WIDTH = NUM_BUCKETS * BUCKET_WIDTH
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
    _left_offset = 0
    _right_offset = 0

    # cursor bucket index or -1 for none
    _cursor_index = -1

    # selection bucket index or -1 for none
    _selection_index = -1

    def __init__(self, master, identified_data, data_preferences):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          selection_data(SelectionData): Various selected data.
          trace_vars(list of Var): Variables to communicate selection change.
        """

        # data variables
        self._identified_data = identified_data
        self._data_preferences = data_preferences

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

        # add the offset range
        self._range_label = tkinter.Label(self.frame, text="Not selected")
        self._range_label.pack(side=tkinter.TOP, anchor="w")

        # add the byte offset label
        self._byte_offset_label = tkinter.Label(self.frame, text="Not selected")
        self._byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the selected byte offset label
        self._selected_byte_offset_label = \
                           tkinter.Label(self.frame, text="Not selected")
        self._selected_byte_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the zoom bar PhotoImage
        l = tkinter.Label(self.frame, image=self._photo_image,
                          relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)

        # bind events
#        l.bind('<Any-Motion>', self._handle_mouse_drag)
#        l.bind('<Button-1>', self._handle_mouse_click)
#        l.bind('<Enter>', self._handle_mouse_drag)
#        l.bind('<Leave>', self._handle_leave_window)

        # initial zoomed-out variables
        self._start_offset = 0
        self._bytes_per_bucket = self._identified_data.image_size / \
                                                           self.NUM_BUCKETS

        self._draw()

    # draw
    def _draw(self):
        """Draw the offset values and the zoom bar."""
 
        # create the bucket data
        data = [0] * (self.NUM_BUCKETS)
        filtered_data = [0] * (self.NUM_BUCKETS)

        # calculate the histograms
        for key in self._identified_data.forensic_paths:
            offset = int(key)
            index = int((offset - self._start_offset) / self._bytes_per_bucket)
        if (index >= 0 and index < self.NUM_BUCKETS):
            data[index] += 1

        # put in the offset range text
        stop_offset = int(self._start_offset +
                          self._bytes_per_bucket * self.NUM_BUCKETS)
        if stop_offset > self._identified_data.image_size:
            stop_offset = self._identified_data.image_size
        self._range_label["text"] = \
                           "Range: " + offset_string(self._start_offset) + \
                           " to " + offset_string(stop_offset)

        # put in the byte offset text


        # clear the PhotoImage
        self._photo_image.put("gray", to=(0, 0, self.ZOOM_BAR_WIDTH,
                                                self.ZOOM_BAR_HEIGHT))

        # draw the selection line
        if self._selection_index != -1:
            x=self._selection_index * self.BUCKET_WIDTH
            self._photo_image.put("red", to=(x,0,x+self.BUCKET_WIDTH,
                                             self.BUCKET_HEIGHT))

        # draw the cursor line
        if self._cursor_index != -1:
            x=self._cursor_index * self.BUCKET_WIDTH
            self._photo_image.put("red3", to=(x,0,x+self.BUCKET_WIDTH,
                                              self.BUCKET_HEIGHT))

        # draw the bucket lines
        bar_color = "#000066"
        for i in range(self.NUM_BUCKETS):
            x=i * self.BUCKET_WIDTH
            y = data[i] if (data[i] < self.MAX_HISTOGRAM_HEIGHT) else \
                                                 self.MAX_HISTOGRAM_HEIGHT
            self._photo_image.put(bar_color, to=(x,0,x+self.BUCKET_WIDTH, y))





    # set the view based on identified data and selection data
    def _set_data(self, identified_data):
        """Args:
          identified_data (IdentifiedData): All the identified data about
            the scan.
        """

        # sector size
        self._sector_size = identified_data.sector_size

        # total sectors
        self._total_sectors = (
              (identified_data.image_size + (identified_data.sector_size - 1))
              // identified_data.sector_size)

        # sectors per index
        self._sectors_per_index = self._total_sectors / self.MATRIX_ORDER**2
        if self._sectors_per_index < 1.0:
            self._sectors_per_index = 1.0

        # set data points
        for key in identified_data.forensic_paths:
            sector = int(key) // identified_data.sector_size
            subscript = int(sector // self._sectors_per_index)
            if self._data[subscript] < 12:
                self._data[subscript] += 1

        # plot the data points
        for i in range(self.MATRIX_ORDER**2):
            if i * self._sectors_per_index > self._total_sectors:
                # index reached end of image
                break
            self._draw_cell(i)

    # highlight a cell being hovered over by the mouse
    def _set_highlight_index(self, i):

        # clear old highlight
        if self._highlight_index != -1:
            old_index = self._highlight_index
            self._highlight_index = -1
            self._draw_cell(old_index)

        # set new highlight
        self._highlight_index = i
        if i != -1:
            # use new selection
            self._draw_cell(i)
            byte_offset = int(i * self._sectors_per_index) * self._sector_size
            self.offset_label['text'] = "Byte offset: " + \
                                                  offset_string(byte_offset)
        else:
            # clear to -1
            self.offset_label['text'] = "Byte offset: Not selected"

    # select a cell being clicked on by the mouse
    def _set_selection_index(self, i):

        # clear old selection
        if self._selection_index != -1:
            old_index = self._selection_index
            self._selection_index = -1
            self._draw_cell(old_index)

        # set new selection
        self._selection_index = i
        if i != -1:
            # new selection
            offset = int(i * self._sectors_per_index) * self._sector_size
            self._image_overview_byte_offset_selection_trace_var.set(offset)
            self._draw_cell(i)
            self.selected_offset_label['text'] = \
                        "Selected byte offset: " + offset_string(offset)

        else:
            # clear to -1
            self._image_overview_byte_offset_selection_trace_var.set(-1)
            self.selected_offset_label['text'] = \
                                     "Selected byte offset: Not selected"

    # draw cell at index i considering _highlight_index and _selection_index
    def _draw_cell(self, i):
        x=(i%self.MATRIX_ORDER) * self.POINT_SIZE
        y=(i//self.MATRIX_ORDER) * self.POINT_SIZE
        cell_color = self._colors[self._data[i]]
        if i == self._highlight_index: border_color = "red"
        elif i == self._selection_index: border_color = "red3"
        else: border_color = None

        # draw cell
        if border_color is not None:
            # first draw cell using border color
            self._photo_image.put(border_color,
                        to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))

            # then draw inner part of box with existing cell color
            self._photo_image.put(cell_color,
                        to=(x+1, y+1, x+self.POINT_SIZE-1, y+self.POINT_SIZE-1))
        else:
            # draw regular cell
            self._photo_image.put(cell_color,
                            to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))

    # convert mouse coordinate to data subscript or -1 if out of image range
    def _mouse_to_index(self, e):
        # get index from mouse
        x = int((e.x - 2) // self.POINT_SIZE)
        if x < 0: x=0
        if x >= self.MATRIX_ORDER: x = self.MATRIX_ORDER - 1
        y = int((e.y - 2) // self.POINT_SIZE)
        if y < 0: y=0
        if y >= self.MATRIX_ORDER: y = self.MATRIX_ORDER - 1
        i = x + y * self.MATRIX_ORDER

        # set index to -1 if outside of image range
        if i * self._sectors_per_index > self._total_sectors:
            i = -1

        # return validated index
        return i

    def _handle_mouse_drag(self, e):
        i = self._mouse_to_index(e)
        self._set_highlight_index(i)

    def _handle_leave_window(self, e):
        self._set_highlight_index(-1)

    def _handle_mouse_click(self, e):
        i = self._mouse_to_index(e)
        self._set_selection_index(i)

