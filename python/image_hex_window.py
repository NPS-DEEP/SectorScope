import tkinter 
import be_image_reader
from forensic_path import offset_string

class ImageHexWindow():
    """Provides a window to show a hex dump of specified bytes of a
    media image.
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
        self.LINESIZE = 16
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection

        # state
        self._hash_state = None # filtered, unfiltered, unmatched

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Hex View")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._close)

        # add the frame to contain the color legend
        # add the color legend
        f = tkinter.Frame(self._root_window)
        f.pack(side=tkinter.TOP, pady=4)
        tkinter.Label(f,text="   ",background="#660000").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Not filtered      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#004400").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Filtered      ").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="   ",background="#ccccff").pack(side=tkinter.LEFT)
        tkinter.Label(f,text="Not matched").pack(side=tkinter.LEFT)


        # add the frame to contain the hex text and the scrollbar
        hex_frame = tkinter.Frame(self._root_window, bd=1,
                                             relief=tkinter.SUNKEN)
        hex_frame.pack(side=tkinter.TOP, anchor="w")

        # scrollbar
        scrollbar = tkinter.Scrollbar(hex_frame, bd=0)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # add the text containing the plot image
        HEX_TEXT_WIDTH=88
        HEX_TEXT_HEIGHT=32
        self._hex_text = tkinter.Text(hex_frame, width=HEX_TEXT_WIDTH,
                                      height=HEX_TEXT_HEIGHT, bd=0,
                                      yscrollcommand=scrollbar.set)
        self._hex_text.pack()

        scrollbar.config(command=self._hex_text.yview)

        # tags available for the hex text lines
        self._hex_text.tag_config("even_unmatched", background="#eeeeff")
        self._hex_text.tag_config("odd_unmatched", background="#ddddff")
        self._hex_text.tag_config("even_filtered", background="#ccffcc")
        self._hex_text.tag_config("odd_filtered", background="#aaffaa")
        self._hex_text.tag_config("even_filtered", background="#ccffcc")
        self._hex_text.tag_config("odd_filtered", background="#aaffaa")
        self._hex_text.tag_config("even_unfiltered", background="#ffdddd")
        self._hex_text.tag_config("odd_unfiltered", background="#ffcccc")
        self._hex_text.tag_config("outside_block", background="white")

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection)
        self._root_window.withdraw()

    def _close(self):
        self._root_window.withdraw()

    def _get_hash_match_state(self):
        # match state is filtered, unfiltered, or unmatched

        # get selected block hash value
        block_hash = self._offset_selection.block_hash

        # hash was not matched
        if block_hash not in self._identified_data.hashes:
            return "unmatched"

        # hash was matched
        # see hash_histogram_bar _calculate_hash_counts for filter reference
        sources = self._identified_data.hashes[block_hash]

        # count exceeds max_hashes
        if self._filters.max_hashes != 0 and count > self._filters.max_hashes:
            return "filtered"

        # hash is filtered
        if block_hash in self._filters.filtered_hashes:
            return "filtered"

        # a source is flagged or a source itself is filtered
        else:
            for source in sources:
                if self._filters.filter_flagged_blocks and "label" in source:
                    # source has a label flag
                    return "filtered"
                if source["source_id"] in self._filters.filtered_sources:
                    # a source is filtered
                    return "filtered"

        # not filtered
        return "unfiltered"

    def _get_line_tag(self, i):
        # return the line tag associated with the match and line state
        if i >= self._identified_data.block_size:
            return "outside_block"

        if self._match_state == "filtered":
            if (i / self.LINESIZE) % 2 == 0:
                return "even_filtered"
            else:
                return "odd_filtered"
        if self._match_state == "unfiltered":
            if (i / self.LINESIZE) % 2 == 0:
                return "even_unfiltered"
            else:
                return "odd_unfiltered"
        if self._match_state == "unmatched":
            if (i / self.LINESIZE) % 2 == 0:
                return "even_unmatched"
            else:
                return "odd_unmatched"
        raise RuntimeError("program error")

    def _handle_filter_change(self, *args):
        self._set_view()

    def _handle_offset_selection(self, *args):
        self._set_view()

    def _set_view(self):

        # clear any existing view
        self._hex_text.delete(1.0, "end")

        # get offset from _offset_selection
        offset = self._offset_selection.offset

        # set hex view
        if offset == -1:
            # disable the text area
            self._hex_text.config(state=tkinter.DISABLED)

        else:
            # get match state
            self._match_state = self._get_hash_match_state()

            # enable the text area
            self._hex_text.config(state=tkinter.NORMAL)

            # read page of image bytes starting at offset
            buf = be_image_reader.read(self._identified_data.image_filename,
                                                       offset, self.PAGESIZE)

            # set hex view for one line
            self._set_lines(offset, buf)

            # make visible if not already
            self._root_window.deiconify()

    def _set_lines(self, offset, buf):
        # format bytes into the hex text view
        for i in range(0, self.PAGESIZE, self.LINESIZE):
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

            # get the tag for this line
            line_tag = self._get_line_tag(i)

            # add this composed line
            self._hex_text.insert(tkinter.END, line, line_tag)

