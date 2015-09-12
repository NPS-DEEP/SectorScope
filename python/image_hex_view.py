import tkinter 
import hashlib
import be_image_reader
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip

class ImageHexView():
    """Prints a banner and shows a hex dump of specified bytes of a
    media image.

    Attributes:
      frame(Frame): the containing frame for this view.
      _image_reader (BEImageReader): an optimized bulk_extractor media
        image reader.
    """

    def __init__(self, master, identified_data, filters, offset_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
        """
        # variables
        self.PAGESIZE = 16384 # 2^14
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection
        self._selected_hash = ""

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(self.frame, text='Image Hex View') \
                      .pack(side=tkinter.TOP)

        # add the annotation frame
        annotation_frame = tkinter.Frame(self.frame)
        annotation_frame.pack(side=tkinter.TOP, anchor="w")

        # add the offset and hash frame to the annotation frame
        selection_frame = tkinter.Frame(annotation_frame)
        selection_frame.pack(side=tkinter.LEFT)

        # add the image offset text to the offset and hash frame
        self.image_offset_label = tkinter.Label(selection_frame,
                                 text='Image offset: not selected')
        self.image_offset_label.pack(side=tkinter.TOP, anchor="w")

        # add the block hash frame to the offset and hash frame
        block_hash_frame = tkinter.Frame(selection_frame)
        block_hash_frame.pack(side=tkinter.TOP, anchor="w")

        # block_hash_frame "block hash" text
        tkinter.Label(block_hash_frame, text='Block Hash:').pack(
                                              side=tkinter.LEFT, anchor="w")

        # block_hash_frame block hash entry value
        self._hash_label = tkinter.Label(block_hash_frame, width=40, anchor="w")
        self._hash_label.pack(side=tkinter.LEFT)

        # add the hash filter frame to the filter and ID frame
        hash_filter_frame = tkinter.Frame(annotation_frame)
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

        # add the source ID frame
        source_id_frame = tkinter.Frame(self.frame)
        source_id_frame.pack(side=tkinter.TOP, anchor="w")

        # add "Source ID:" text to the source ID frame
        tkinter.Label(source_id_frame, text="Source ID:").pack(
                                                           side=tkinter.LEFT)

        # add the source ID label
        self._source_id_label = tkinter.Label(source_id_frame,
                                 text="Not selected", width=72, anchor="w")
        self._source_id_label.pack(side=tkinter.TOP, anchor="w")

        # add the frame to contain the hex text and the scrollbar
        hex_frame = tkinter.Frame(self.frame, bd=1, relief=tkinter.SUNKEN)

        # scrollbar
        scrollbar = tkinter.Scrollbar(hex_frame, bd=0)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # add the text containing the plot image
        HEX_TEXT_WIDTH=88
        HEX_TEXT_HEIGHT=24
        self._hex_text = tkinter.Text(hex_frame, width=HEX_TEXT_WIDTH,
                                      height=HEX_TEXT_HEIGHT, bd=0,
                                      yscrollcommand=scrollbar.set)
        self._hex_text.pack()

        scrollbar.config(command=self._hex_text.yview)
        hex_frame.pack(side=tkinter.TOP, anchor="w")

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_set_data)

        # set view for no data
        self._handle_set_data()

    # set variables and the image based on identified_data when
    # _offset_selection changes
    def _handle_set_data(self, *args):
        # parameter *args is required by IntVar callback

        # get offset from _offset_selection
        offset = self._offset_selection.offset

        # clear views if no data
        if offset == -1:
            self._set_no_data()
            self._add_hash_button.config(state=tkinter.DISABLED)
            self._remove_hash_button.config(state=tkinter.DISABLED)
            return

        # set offset value
        self._set_offset_value(offset)

        # read page of image bytes starting at offset
        buf = be_image_reader.read(self._identified_data.image_filename,
                                                       offset, self.PAGESIZE)

        # set the selected hash
        self._selected_hash = self._calculate_block_hash(buf)

        # put the hash in the hash label
        self._hash_label['text'] = self._selected_hash

        # set state for buttons
        self._set_add_and_remove_button_states()

        # set any source ID values
        self._set_source_id_values()

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

    def _set_source_id_values(self):
        # get the source ID text
        if not self._selected_hash in self._identified_data.hashes:
            source_text = "Not selected"
        else:
            sources = self._identified_data.hashes[self._selected_hash]
            source_ids = set()
            for source in sources:
                source_ids.add(source["source_id"])

            if len(source_ids) == 0:
                source_text = "None"
            else:
                source_text = " ".join(str(u) for u in source_ids)

        # put the source ID text into the source ID label
        self._source_id_label['text'] = source_text

    def _set_no_data(self):
        # clear image offset text
        self.image_offset_label['text'] = "Image offset: Not selected"

        # clear hash field
        self._hash_label['text'] = "Not selected"
        self._selected_hash = ""

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

    # button changes filter
    def _handle_add_hash_to_filter(self):
        self._filters.filtered_hashes.add(self._selected_hash)
        self._filters.fire_change()

    # button changes filter
    def _handle_remove_hash_from_filter(self):
        self._filters.filtered_hashes.remove(self._selected_hash)
        self._filters.fire_change()

    # identified_data changes views
    def _handle_identified_data_change(self, *args):
        self._set_no_data()

    # filter changes views
    def _handle_filter_change(self, *args):
        self._set_add_and_remove_button_states()
        self._set_source_id_values()

