from scrolled_text import ScrolledText
import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ImageHexTable():
    """Manages the hex view for a selected range into a media image.
    The hex view changes when the range selection changes.

    Attributes:
      frame(Frame): the containing frame for the hex table.
      _hex_text(Text): The Text widget to render the hex table in.
    """
    def __init__(self, master, data_manager, histogram_control,
                                                        width=88, height=32):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
        """
        # variables
        self.PAGESIZE = 16384 # 2^14
        self.LINESIZE = 16
        self._data_manager = data_manager
        self._histogram_control = histogram_control

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # scrolled frame for the hex text
        scrolled_text = ScrolledText(self.frame, width=width, height=height)
        scrolled_text.scroll_frame.pack(side=tkinter.TOP)

        # the hex text to draw the hex data in
        self._hex_text = scrolled_text.text

        # tags available for the hex text lines
        # states are: unmatched=gray, matched=blue, ignored=red,
        # highlighted=green, outside=white
        self._hex_text.tag_config("even_unmatched",
                                             background=colors.EVEN_UNMATCHED)
        self._hex_text.tag_config("odd_unmatched",
                                             background=colors.ODD_UNMATCHED)
        self._hex_text.tag_config("even_matched",
                                             background=colors.EVEN_MATCHED)
        self._hex_text.tag_config("odd_matched",
                                             background=colors.ODD_MATCHED)
        self._hex_text.tag_config("outside_block", background="white")

    def _get_line_tag(self, i, is_in):
        # return the line tag associated with the match and line state
        if i >= self._data_manager.hash_block_size:
            # index is outside of block range
            return "outside_block"
        elif is_in:
            # hash is in dataset
            if (i / self.LINESIZE) % 2 == 0:
                return "even_matched"
            else:
                return "odd_matched"
        else:
            # hash is not in dataset
            if (i / self.LINESIZE) % 2 == 0:
                return "even_unmatched"
            else:
                return "odd_unmatched"

    def clear_view(self):
        # clear any existing view
        self._hex_text.delete(1.0, "end")

    def set_view(self, offset, buf, is_in):
        # clear any existing view
        self._hex_text.delete(1.0, "end")

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
            line_tag = self._get_line_tag(i, is_in)

            # add this composed line
            self._hex_text.insert(tkinter.END, line, line_tag)

