import tkinter 
from forensic_path import offset_string

class ImageOverviewPlot():
    """Prints a banner and plots an image overview of matched blocks
    given an IdentifiedData data structure.

    Plot points with a higher match density are shown darker than points
    with a lower match density.

    Clicking on a plot point sets the image offset in the IntVar variable
    provided.

    Attributes:
      frame(Frame): the containing frame for this plot.
      _photo_image(PhotoImage): Exists solely to keep the image from being
        garbage collected.
      _image_overview_byte_offset_selection_trace_var(IntVar): Setting this
        alerts listeners to the new selection.
    """

    # order of the 2D square matrix
    MATRIX_ORDER = 100

    # pixels per data point
    POINT_SIZE = 3

    # plot size in pixels
    PLOT_SIZE = MATRIX_ORDER * POINT_SIZE

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

    # highlight index or -1 for none
    _highlight_index = -1

    # selection index or -1 for none
    _selection_index = -1

    def __init__(self, master, identified_data,
                 image_overview_byte_offset_selection_trace_var):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          image_overview_byte_offset_selection_trace_var(IntVar): Variable to
            communicate the image byte offset selected upon mouse click.
        """

        # the photo_image
        self._photo_image = tkinter.PhotoImage(width=self.PLOT_SIZE,
                                               height=self.PLOT_SIZE)
        self._photo_image.put("gray", to=(0, 0, self.PLOT_SIZE, self.PLOT_SIZE))

        # set general data and the image
        self._set_data(identified_data)

        # define the selection variable
        self._image_overview_byte_offset_selection_trace_var = \
                              image_overview_byte_offset_selection_trace_var

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(self.frame, text='Image Density Overview') \
                      .pack(side=tkinter.TOP)
        self.offset_label = tkinter.Label(self.frame,
                                 text='Byte offset: not selected')
        self.offset_label.pack(side=tkinter.TOP, anchor="w")
        self.selected_offset_label = tkinter.Label(self.frame,
                                 text='Selected byte offset: not selected')
        self.selected_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the overview plot image
        l = tkinter.Label(self.frame, image=self._photo_image,
                          relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)
        l.bind('<Any-Motion>', self._handle_mouse_drag)
        l.bind('<Button-1>', self._handle_mouse_click)
        l.bind('<Enter>', self._handle_mouse_drag)
        l.bind('<Leave>', self._handle_leave_window)

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
        if self._blocks_per_index < 1.0:
            self._blocks_per_index = 1.0

        # set data points
        for key in identified_data.forensic_paths:
            block = int(key) // identified_data.block_size
            subscript = int(block // self._blocks_per_index)
            if self._data[subscript] < 12:
                self._data[subscript] += 1

        # plot the data points
        for i in range(self.MATRIX_ORDER**2):
            if i * self._blocks_per_index > self._total_blocks:
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
            byte_offset = int(i * self._blocks_per_index) * self._block_size
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
            offset = int(i * self._blocks_per_index) * self._block_size
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
        if i * self._blocks_per_index > self._total_blocks:
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

