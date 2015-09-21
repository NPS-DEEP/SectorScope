import tkinter
import hashlib
from be_image_reader import read

class OffsetSelection():
    """Manage a byte offset selection.

    Registered callbacks are called when cleared.

    _offset_selection_changed is used as a signal.
    Its value is always true.

    Attributes:
      offset(int): selection or -1 for not selected.
      block_hash(str): The MD5 hexdigest calculated at this offset,
        zero extended.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    offset = -1
    block_hash = None

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._offset_selection_changed = tkinter.BooleanVar()

    def set(self, image_file, offset, block_size):
        # set offset
        self.offset = offset

        # read buffer to calcualte block hash
        buf = read(image_file, offset, block_size)

        # calculate the MD5 from the block of data in buf
        m = hashlib.md5()
        m.update(buf[:block_size])
        if len(buf) < block_size:
            # zero-extend the short block
            m.update(bytearray(block_size - len(buf)))
        self.block_hash = m.hexdigest()

        # signal change
        self._offset_selection_changed.set(True)

    def clear(self):
        self.offset = -1
        self.block_hash = None

        # signal change
        self._offset_selection_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on offset selection change."""
        self._offset_selection_changed.trace_variable('w', f)

