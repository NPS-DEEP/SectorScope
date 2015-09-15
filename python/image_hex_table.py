import tkinter 
import be_image_reader
from scrolled_text import ScrolledText

class ImageHexTable():
    """Manages the hex view for a selected offset into a media image.
    The hex view changes when the offset selection changes.

    Attributes:
      frame(Frame): the containing frame for the hex table.
      _hex_text(Text): The Text widget to render the hex table in.
 
    """
    def __init__(self, master, identified_data, filters, offset_selection,
                 *, width=88, height=32):
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

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # scrolled frame for the hex text
        scrolled_text = ScrolledText(self.frame, width=width, height=height)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the hex text to draw the hex data in
        self._hex_text = scrolled_text.text

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

        # Note that filter change is not sufficient to deiconify,
        # but offset selection is.

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

            # write the hex lines
            self._set_lines(offset, buf)

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

