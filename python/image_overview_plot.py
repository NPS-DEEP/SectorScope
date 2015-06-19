import tkinter 

class ImageOverviewPlot():
    """Prints a banner and plots an image overview of matched blocks
    given an IdentifiedData data structure.

    Plot points with a higher match density are shown darker than points
    with a lower match density.

    Clicking on a plot point sets the image offset in the IntVar variable
    provided.

    Attributes:
      _photo_image(PhotoImage): Exists solely to keep the image from being
        garbage collected.
      _rescaler(float): Convert from image offset to plot index.
      _selected_byte_offset(IntVar): Set this alerts listeners to new selection.
    """

    # order of the 2D square matrix
    MATRIX_ORDER = 100

    # pixels per data point
    POINT_SIZE = 4

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

    # the data array
    _data = [0] * (MATRIX_ORDER**2)

    # the old selection index or -1 for none
    _old_selection_index = -1

    def __init__(self, master, identified_data, selected_byte_offset):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All the identified data about
            the scan.
          selected_byte_offset(IntVar): Variable communicates the image byte
            offset selected upon mouse click.
        """

        # the photo_image
        PLOT_SIZE = self.MATRIX_ORDER * self.POINT_SIZE
        self._photo_image = tkinter.PhotoImage(width=PLOT_SIZE, height=PLOT_SIZE)

        # set general data and the image
        self._set_data(identified_data)

        # define the selection variable
        self._selected_byte_offset = selected_byte_offset

        # make the containing frame
        f = tkinter.Frame(master)

        # add the header text
        tkinter.Label(f, text='Image Overview') \
                      .pack(side=tkinter.TOP)
        tkinter.Label(f, text='Image: %s'%identified_data.image_filename) \
                      .pack(side=tkinter.TOP, anchor="w")
        self.offset_label = tkinter.Label(f,
                                 text='Byte offset: not selected')
        self.offset_label.pack(side=tkinter.TOP, anchor="w")
        self.selected_offset_label = tkinter.Label(f,
                                 text='Selected byte offset: not selected')
        self.selected_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the overview plot image
        l = tkinter.Label(f, image=self._photo_image, relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP, padx=5,pady=5)
        l.bind('<Any-Motion>', self._handle_mouse_drag)
        l.bind('<Button-1>', self._handle_mouse_click)
        l.bind('<Enter>', self._handle_mouse_drag)
        l.bind('<Leave>', self._handle_leave_window)

        # pack the frame
        f.pack()

    # set variables and the image based on identified_data
    def _set_data(self, identified_data):
        """Args:
          identified_data (IdentifiedData): All the identified data about
            the scan.
        """

        # block size
        self._block_size = identified_data.block_size

        # total blocks
        self._total_blocks = (
              (identified_data.image_size + (identified_data.block_size - 1))
              // identified_data.block_size)

        # blocks per index
        self._blocks_per_index = self._total_blocks / self.MATRIX_ORDER**2
        if self._blocks_per_index < 1:
            self._blocks_per_index = 1


        # rescaler for going from media image offset to data index
        self._rescaler = self.MATRIX_ORDER**2 / identified_data.image_size

        # if the matrix is larger than the image then clip the rescaler
        if self._rescaler > 1.0:
            self._rescaler = 1.0

        # set data points
        for key in identified_data.forensic_paths:
            block = int(key) // identified_data.block_size
            subscript = int(block // self._blocks_per_index)
            if self._data[subscript] < 12:
                self._data[subscript] += 1

        # plot the data points
        for i in range(self.MATRIX_ORDER**2):
            self._draw_cell(i)

    # convert mouse coordinate to data subscript
    def _mouse_to_index(self, e):
        x = int((e.x - 2) // self.POINT_SIZE)
        if x < 0: x=0
        if x >= self.MATRIX_ORDER: x = self.MATRIX_ORDER - 1
        y = int((e.y - 2) // self.POINT_SIZE)
        if y < 0: y=0
        if y >= self.MATRIX_ORDER: y = self.MATRIX_ORDER - 1
        return x + y * self.MATRIX_ORDER

    def _draw_cell(self, i):
        point_color = self._colors[self._data[i]]
        x=(i%self.MATRIX_ORDER) * self.POINT_SIZE
        y=(i//self.MATRIX_ORDER) * self.POINT_SIZE
        if i * self._blocks_per_index <= self._total_blocks:
            # valid range for data
            self._photo_image.put(point_color,
                            to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))
        else:
            # invalid range so draw gray cell instead
            self._photo_image.put("gray",
                            to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))

    def _draw_highlighted_cell(self, i):
        if i * self._blocks_per_index > self._total_blocks:
            # not valid range for data
            return

        # set pixel coordinates
        x=(i%self.MATRIX_ORDER) * self.POINT_SIZE
        y=(i//self.MATRIX_ORDER) * self.POINT_SIZE

        # first draw cell as highlight color
        self._photo_image.put("red",
                        to=(x, y, x+self.POINT_SIZE, y+self.POINT_SIZE))

        # then draw inner part of box with existing cell color
        point_color = self._colors[self._data[i]]
        self._photo_image.put(point_color,
                        to=(x+1, y+1, x+self.POINT_SIZE-1, y+self.POINT_SIZE-1))

    def _handle_mouse_drag(self, e):
        i = self._mouse_to_index(e)
        #print("e ",e.x,e.y, i, e.widget)
        byte_offset = int(i * self._blocks_per_index) * self._block_size
        self.offset_label['text'] = "Byte offset: %s" % byte_offset

        # skip if no change
        if i is self._old_selection_index:
            return

        # unselect old
        if self._old_selection_index is not -1:
            self._draw_cell(self._old_selection_index)

        # select new
        self._old_selection_index = i
        self._draw_highlighted_cell(i)

    def _handle_leave_window(self, e):
        print("LEAVE", e.widget)

        # zz
        return

        # unselect old
        if self._old_selection_index is not -1:
            self._draw_cell(self._old_selection_index)
            self._old_selection_index = -1

    def _handle_mouse_click(self, e):
        i = self._mouse_to_index(e)
        self._selected_byte_offset = int(i * self._blocks_per_index) * \
                                     self._block_size
        self.selected_offset_label['text'] = \
                      "Selected byte offset: %s" % self._selected_byte_offset
                                    
        print("Byte offset ", self._selected_byte_offset)

