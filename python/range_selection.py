from sys import maxsize
import hashlib
from show_error import ShowError
from be_image_reader import read
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class RangeSelection():
    """Manage range selection, MD5, and image buffer.  Offsets should
      already be sector aligned.

    Registered callbacks are called when range is set or cleared.

    _range_selection_changed is used as a signal.
    Its value is always true.

    Attributes:
      is_selected(bool): Whether a range is selected.
      start_offset(int): Start offset of range.
      stop_offset(int): Start offset of range.
      block_hash(str): The MD5 hexdigest calculated at this offset,
        zero extended.
      block_hash_is_in(bool): Whether block_hash is in identified_data.
      block_hash_offset(int): The offset to the block hash.
      buf_offset(int): The byte offset of the media image buffer
      buf(bytearray): The media image buffer.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    BUFSIZE = 16384 # 2^14

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._range_selection_changed = tkinter.BooleanVar()
        self._clear()

    def _clear(self):
        self.is_selected = False
        self.start_offset = 0
        self.stop_offset = 0
        self.block_hash = ""
        self.block_hash_is_in = False
        self.block_hash_offset = 0
        self.buf = bytearray()

    # return lowest path in start_offset <= path < stop_offset else -1
    def _first_path(self, master, identified_data, start_offset, stop_offset):
        first_path = maxsize
        for forensic_path, block_hash in \
                               identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_offset and offset < stop_offset and \
                                                       offset < first_path:
                first_path = offset

        if first_path == maxsize:
            return (start_offset, False)
        else:
            return (first_path, True)

    def set(self, master, identified_data, offset1, offset2):
        """Set offsets.  Input can be out of order.  Equal offsets clears."""

        # clear when equal
        if offset1 == offset2:
            self.clear()
            return

        # set is_selected
        self.is_selected = True

        # set start_offset, stop_offset
        if offset1 < offset2:
            self.start_offset = offset1
            self.stop_offset = offset2
        else:
            self.start_offset = offset2
            self.stop_offset = offset1

        # find first block hash offset
        (self.block_hash_offset, self.block_hash_is_in) = self._first_path(
                                        master, identified_data,
                                        self.start_offset, self.stop_offset)

        # read page of image bytes starting at offset else warn and clear
        try:
            self.buf = read(identified_data.image_filename,
                                       self.block_hash_offset, self.BUFSIZE)
        except Exception as e:
            ShowError(master, "Open Error", e)
            self.clear()
            return

        # calculate the MD5 from the block of data in buf
        m = hashlib.md5()
        m.update(self.buf[:identified_data.block_size])
        if len(self.buf) < identified_data.block_size:
            # zero-extend the short block
            m.update(bytearray(identified_data.block_size - len(self.buf)))
        self.block_hash = m.hexdigest()

        # signal change
        self._range_selection_changed.set(True)

    def clear(self):
        self._clear()
        
        # signal change
        self._range_selection_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on range selection change."""
        self._range_selection_changed.trace_variable('w', f)

