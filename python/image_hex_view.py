import tkinter 
from be_image_reader import BEImageReader
from forensic_path import offset_string

class ImageHexView():
    """Prints a banner and shows a hex dump of specified bytes of a
    media image.

    Attributes:
      _image_filename (string): The media image whose bytes are being read
        and viewed.
      _image_detail_byte_offset_selection (IntVar): This variable has the
        currently selected image offset.
      _image_reader (BEImageReader): an optimized bulk_extractor media
        image reader.
      _hex_text (Text): the text widget that the hex text goes into.
    """

    def __init__(self, master, image_filename,
                 image_detail_byte_offset_selection):
        """Args:
          master(a UI container): Parent.
          image_filename(string): media image filename
          image_detail_byte_offset_selection(IntVar): the byte offset
            selected in the image detail plot
        """
        # variables
        self._image_filename = image_filename
        self._image_detail_byte_offset_selection = \
                                          image_detail_byte_offset_selection
        self._image_reader = BEImageReader(image_filename)

        # make the containing frame
        outer_frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(outer_frame, text='Image Hex View') \
                      .pack(side=tkinter.TOP)
        self.image_offset_label = tkinter.Label(outer_frame,
                                 text='Image offset: not selected')
        self.image_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the frame to contain the hex text and the scrollbar
        hex_frame = tkinter.Frame(outer_frame, bd=2, relief=tkinter.SUNKEN)

        # scrollbar
        scrollbar = tkinter.Scrollbar(hex_frame, bd=0)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # add the label containing the plot image
        self._hex_text = tkinter.Text(hex_frame, height=24, width=80, bd=0,
                                yscrollcommand=scrollbar.set)
        self._hex_text.pack()

        scrollbar.config(command=self._hex_text.yview)
        hex_frame.pack()

        # pack the outer frame
        outer_frame.pack(side=tkinter.LEFT, padx=8, pady=8)

        # listen to changes in _image_detail_byte_offset_selection
        image_detail_byte_offset_selection.trace_variable('w', self._set_data)


    # set variables and the image based on identified_data
    def _set_data(self, *args):
        # parameter *args is required by IntVar callback

        # get offset from _image_detail_byte_offset_selection
        offset = self._image_detail_byte_offset_selection.get()

        # clear any existing view
        self._hex_text.delete(1.0, "end")

        # done if no data
        if offset == -1:
            self.image_offset_label['text'] = "Image offset: not selected"
            return

        # write new offset at top
        self.image_offset_label['text'] = \
                                 "Image offset: " + offset_string(offset)

        # read page of image bytes starting at offset
        PAGESIZE = 16385 # 2^14
        LINESIZE = 16
        buf = self._image_reader.read(offset, PAGESIZE)

        # format bytes into the hex text view
        for i in range(0, PAGESIZE, LINESIZE):
            # stop when out of data
            if i >= len(buf):
                 break

            # format image offset
            line = "0x%08x:" % (offset + i)

            # append hexadecimal values
            for j in range(i, i+16):
                if j % 4 == 0:
                    # add spacing between some columns
                    line += ' '

                if j < len(buf):
                    # print the value
                    line += "%02x " % buf[j]
                else:
                    # fill lack of data with space
                    line += "   "

            # append ascii values
            for j in range(i, i+16):
                if j < len(buf):
                    c = buf[j]
                    if (c > 31 and c < 127):
                        # c is printable ascii
                        line += chr(c)
                    else:
                        # not printable ascii
                        line += '.'

            # terminate the line
            line += "\n"

            # add this composed line
            self._hex_text.insert(tkinter.END, line)

