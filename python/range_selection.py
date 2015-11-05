from sys import maxsize
import hashlib
from error_window import ErrorWindow
from be_image_reader import read
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class RangeSelection():
    """Manage range selection, MD5, and image buffer.  Offsets should
      already be block aligned.

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
      source_ids_in_range(set): Set of source IDs in range.
      hashes_in_range(set): Set of hashes in range.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    BUFSIZE = 16384 # 2^14

    source_ids_in_range = set()
    hashes_in_range = set()

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._range_selection_changed = tkinter.BooleanVar()
        self._clear()

    def _clear(self):
        self.is_selected = False

        # range offsets
        self.start_offset = 0
        self.stop_offset = 0

        # hash in range
        self.block_hash = ""
        self.block_hash_is_in = False
        self.block_hash_offset = 0

        # buffer in range
        self.buf = bytearray()

        # set of sources and hashes in range
        self.source_ids_in_range.clear()
        self.hashes_in_range.clear()

    def set(self, master, identified_data, offset1, offset2):
        """Set offsets.  Input can be out of order.  Equal offsets clears."""

        # clear existing data
        self.clear()

        # done if no range
        if offset1 == offset2 or offset1 == offset2 + 1:
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

        # optimization
        start_byte = self.start_offset
        stop_byte = self.stop_offset

        # the first path in the range
        first_path = maxsize

        # iterate through forensic paths and gather data about the range
        hashes = identified_data.hashes
        for forensic_path, block_hash in \
                               identified_data.forensic_paths.items():
            offset = int(forensic_path)

            # skip if out of range
            if offset < start_byte or offset >= stop_byte:
                continue

            # offset is first path if smaller
            if offset < first_path:
                first_path = offset

            # get source ids in range
            # get source IDs associated with this hash
            (_, source_id_set, _, _) = hashes[block_hash]

            # append source IDs from this hash
            if not source_id_set.issubset(self.source_ids_in_range):
                self.source_ids_in_range = self.source_ids_in_range.union(
                                                               source_id_set)

            # get hashes in range
            self.hashes_in_range.add(block_hash)

        # establish first path
        if first_path == maxsize:
            # no matched hash in range
            self.block_hash_offset = start_byte
            self.block_hash_is_in = False
        else:
            self.block_hash_offset = first_path
            self.block_hash_is_in = True

        # read page of image bytes starting at offset else warn and clear
        try:
            self.buf = read(identified_data.image_filename,
                                       self.block_hash_offset, self.BUFSIZE)
        except Exception as e:
            ErrorWindow(master, "Open Error", e)
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

