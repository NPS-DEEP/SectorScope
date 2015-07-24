import tkinter 
import hashlib
from be_image_reader import BEImageReader
from forensic_path import offset_string

class ImageHexView():
    """Prints a banner and shows a hex dump of specified bytes of a
    media image.

    Attributes:
      frame(Frame): the containing frame for this view.
      _image_reader (BEImageReader): an optimized bulk_extractor media
        image reader.
    """

    def __init__(self, master, identified_data, filters, byte_offset_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          byte_offset_selection(IntVar): the byte offset selected in the
            image detail plot
        """
        # variables
        self.PAGESIZE = 16384 # 2^14
        self._identified_data = identified_data
        self._filters = filters
        self._byte_offset_selection = byte_offset_selection
        self._image_reader = BEImageReader(identified_data.image_filename)

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(self.frame, text='Image Hex View') \
                      .pack(side=tkinter.TOP)
        self.image_offset_label = tkinter.Label(self.frame,
                                 text='Image offset: not selected')
        self.image_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the line for the block hash frame containing several parts
        hash_frame = tkinter.Frame(self.frame)
        hash_frame.pack(side=tkinter.TOP, anchor="w")

        # hash_frame "block hash" text
        tkinter.Label(hash_frame, text='Block Hash:').pack(side=tkinter.LEFT,
                                                          anchor="w")

        # hash_frame block hash entry value
        self._hash_label = tkinter.Label(hash_frame, text="Not selected",
                                         width=40, anchor="w")
        self._hash_label.pack(side=tkinter.LEFT)

        # hash filter "Filter:" text
        tkinter.Label(hash_frame, text="Filter:").pack(side=tkinter.LEFT)

        # hash_frame "Add Hash to Filter" button
        self._add_hash_button = tkinter.Button(hash_frame, text="Add",
                                state=tkinter.DISABLED,
                                command=self._handle_add_hash_to_filter)
        self._add_hash_button.pack(side=tkinter.LEFT, padx=8, pady=4)

        # hash_frame "Remove Hash from Filter" button
        self._remove_hash_button = tkinter.Button(hash_frame, text="Remove",
                                state=tkinter.DISABLED,
                                command=self._handle_remove_hash_from_filter)
        self._remove_hash_button.pack(side=tkinter.LEFT, padx=8, pady=4)

        # add the frame to contain the hex text and the scrollbar
        hex_frame = tkinter.Frame(self.frame, bd=1, relief=tkinter.SUNKEN)

        # scrollbar
        scrollbar = tkinter.Scrollbar(hex_frame, bd=0)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # add the label containing the plot image
        HEX_TEXT_WIDTH=94  # 88 is good for Linux, 94 is good for Windows
        HEX_TEXT_HEIGHT=24
        self._hex_text = tkinter.Text(hex_frame, width=HEX_TEXT_WIDTH,
                                      height=HEX_TEXT_HEIGHT, bd=0,
                                      yscrollcommand=scrollbar.set)
        self._hex_text.pack()

        scrollbar.config(command=self._hex_text.yview)
        hex_frame.pack()

        # listen to changes in _byte_offset_selection
        byte_offset_selection.trace_variable('w', self._handle_set_data)

    # set variables and the image based on identified_data when
    # byte_offset_selection changes
    def _handle_set_data(self, *args):
        # parameter *args is required by IntVar callback

        # get offset from _byte_offset_selection
        offset = self._byte_offset_selection.get()

        # clear views if no data
        if offset == -1:
            self._set_no_data()
            self._add_hash_button.config(state=tkinter.DISABLED)
            self._remove_hash_button.config(state=tkinter.DISABLED)
            return

        # set offset value
        self._set_offset_value(offset)

        # read page of image bytes starting at offset
        buf = self._image_reader.read(offset, self.PAGESIZE)

        # set the selected hash
        self._selected_hash = self._calculate_block_hash(buf)

        # put the hash in the hash label
        self._hash_label['text'] = self._selected_hash

        # set state for buttons
        self._set_add_and_remove_button_states()

        # set hex view
        self._set_hex_view(offset, buf)

    def _set_add_and_remove_button_states(self):
        # set enabled state of the add hash button
        if self._selected_hash not in self._filters.filtered_hashes and \
           self._selected_hash in self._identified_data.hashes:
            self._add_hash_button.config(state=tkinter.NORMAL)
        else:
            self._add_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the remove hash button
        if self._selected_hash in self._filters.filtered_hashes:
            self._remove_hash_button.config(state=tkinter.NORMAL)
        else:
            self._remove_hash_button.config(state=tkinter.DISABLED)

    def _set_no_data(self):
        # clear image offset text
        self.image_offset_label['text'] = "Image offset: Not selected"

        # clear hash field
        self._hash_label['text'] = "Not selected"

        # clear hex text
        self._hex_text.delete(1.0, "end")

    def _set_offset_value(self, offset):
        # clear any existing view
        self._hex_text.delete(1.0, "end")

        # write new offset at top
        self.image_offset_label['text'] = \
                                 "Image offset: " + offset_string(offset)

    def _calculate_block_hash(self, buf):
        # calculate the MD5 from the block of data in buf
        block_size = self._identified_data.block_size
        m = hashlib.md5()
        m.update(buf[:block_size])
        if len(buf) < block_size:
            # zero-extend the short block
            m.update(bytearray(block_size - len(buf)))

        # return the hash
        return m.hexdigest()

    def _set_hex_view(self, offset, buf):
        # format bytes into the hex text view
        LINESIZE = 16
        for i in range(0, self.PAGESIZE, LINESIZE):
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

    def _handle_add_hash_to_filter(self):
        self._filters.filtered_hashes.append(self._selected_hash)
        self._set_add_and_remove_button_states()
        self._filters.fire_change()

    def _handle_remove_hash_from_filter(self):
        self._filters.filtered_hashes.remove(self._selected_hash)
        self._set_add_and_remove_button_states()
        self._filters.fire_change()

