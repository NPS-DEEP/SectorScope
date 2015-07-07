import tkinter 
from forensic_path import offset_string

class ImageDetailPlot():
    """Prints a banner and plots an image detail of matched blocks
    starting at an offset defined by _image_overview_byte_offset_selection

    Plot points with less sources are shown darker than points with more
    sources.

    Clicking on a plot point sets _image_detail_byte_offset_selection

    Attributes:
      _photo_image(PhotoImage): Exists solely to keep the image from being
        garbage collected.
      _image_overview_byte_offset_selection(IntVar): Setting this alerts
        listeners to the new selection.
      _image_detail_byte_offset_selection(IntVar): Setting this alerts
        listeners to the new selection.
    """

    # order of the 2D square matrix
    MATRIX_ORDER = 100

    # pixels per data point
    POINT_SIZE = 3

    # plot size in pixels
    PLOT_SIZE = MATRIX_ORDER * POINT_SIZE

    # white, then dark blue to light
    _colors = ["#ffffff",
               "#000033","#000066","#000099","#0000cc","#0000ff",
               "#0033ff","#0066ff","#0099ff","#00ccff","#00ffff",
               "#000066","#000099","#0000cc","#0000ff"]

    # highlight index or -1 for none
    _highlight_index = -1

    # selection index or -1 for none
    _selection_index = -1

    # data
    _data = []

    def __init__(self, master, identified_data,
                 image_overview_byte_offset_selection,
                 image_detail_byte_offset_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          image_overview_byte_offset_selection(IntVar): the byte offset
            selected in the image overview plot
          image_detail_byte_offset_selection(IntVar): the byte offset
            selected in the image detail plot
        """

        # a reference to the identified data
        self._identified_data = identified_data

        # the photo_image
        self._photo_image = tkinter.PhotoImage(
                                 width=self.PLOT_SIZE, height=self.PLOT_SIZE)

        # the selection variables
        self._image_overview_byte_offset_selection = \
                                     image_overview_byte_offset_selection
        self._image_detail_byte_offset_selection = \
                                     image_detail_byte_offset_selection

        # make the containing frame
        f = tkinter.Frame(master)

        # add the header text
        tkinter.Label(f, text='Image Count Detail') \
                      .pack(side=tkinter.TOP)
        self.offset_label = tkinter.Label(f,
                                 text='Byte offset: not selected')
        self.offset_label.pack(side=tkinter.TOP, anchor="w")
        self.selected_offset_label = tkinter.Label(f,
                                 text='Selected byte offset: not selected')
        self.selected_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the label containing the plot image
        l = tkinter.Label(f, image=self._photo_image, relief=tkinter.SUNKEN)
        l.pack(side=tkinter.TOP)
        l.bind('<Any-Motion>', self._handle_mouse_drag)
        l.bind('<Button-1>', self._handle_mouse_click)
        l.bind('<Enter>', self._handle_mouse_drag)
        l.bind('<Leave>', self._handle_leave_window)

        # pack the frame
        f.pack(side=tkinter.LEFT, padx=8, pady=8)

        # listen to changes in _image_overview_byte_offset_selection
        self._image_overview_byte_offset_selection = \
                                   image_overview_byte_offset_selection
        image_overview_byte_offset_selection.trace_variable('w', self._set_data)


    # set variables and the image based on identified_data
    def _set_data(self, *args):
        # parameter *args is required by IntVar callback

        # clear current settings and data
        self._highlight_index = -1
        self._set_selection_index(-1)
        self._data = []
        self._photo_image.put("gray", to=(0, 0, self.PLOT_SIZE, self.PLOT_SIZE))

        # value is -1 when not in use
        if self._image_overview_byte_offset_selection.get() == -1:
            return

        # starting block number in range
        self._first_block = int(
                         self._image_overview_byte_offset_selection.get() /
                         self._identified_data.block_size)

        # last block number in range, which may be smaller than matrix
        self._last_block = (((self._identified_data.image_size +
                            (self._identified_data.block_size - 1))
                            // self._identified_data.block_size)) - 1
        if self._last_block >= self._first_block + self.MATRIX_ORDER**2:
            self._last_block = self._first_block + self.MATRIX_ORDER**2 - 1

        # allocate sized data array
        self._data = [0] * (self._last_block + 1 - self._first_block)

        # set data points
        for key in self._identified_data.forensic_paths:
            block = int(key) // self._identified_data.block_size
            if block < self._first_block or block > self._last_block:
                # out of range
                continue

            # set data subscript to count clipped at lightest color used
            subscript = block - self._first_block
            count = len(self._identified_data.forensic_paths[key])
            if count > 14:
                count = 14
            self._data[subscript] = count

        # plot the data points
        for i in range(len(self._data)):
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
            byte_offset = (i + self._first_block) * \
                          self._identified_data.block_size
            self.offset_label['text'] = "Byte offset: " \
                                                + offset_string(byte_offset)
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
            self._image_detail_byte_offset_selection.set(
                  (i + self._first_block) * self._identified_data.block_size)
            self._draw_cell(i)
            self.selected_offset_label['text'] = "Selected byte offset: " \
                               + offset_string(
                               self._image_detail_byte_offset_selection.get())

        else:
            # clear to -1
            self._image_detail_byte_offset_selection.set(-1)
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
        if i >= len(self._data):
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

