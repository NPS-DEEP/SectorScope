from media_hex_table import MediaHexTable
import hashlib
from helpers import read_media_bytes
from error_window import ErrorWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class MediaHexWindow():
    """Provides a window to show a hex dump of specified bytes of a
    media image.
    """

    BUFSIZE = 16384 # 2^14

    def __init__(self, master, data_manager, histogram_control):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
        """
        # variables
        self._is_visible = False
        self._data_manager = data_manager
        self._histogram_control = histogram_control

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Hex View")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._hide)

        # add the annotation label
        self._annotation_label = tkinter.Label(self._root_window)
        self._annotation_label.pack(side=tkinter.TOP)

        # add the MD5 value label
        self._md5_label = tkinter.Label(self._root_window)
        self._md5_label.pack(side=tkinter.TOP)

        # add the frame to contain the media hex table
        self._media_hex_table = MediaHexTable(self._root_window, data_manager,
                                      histogram_control, width=88, height=32)
        self._media_hex_table.frame.pack(side=tkinter.TOP, anchor="w")

        # register to receive histogram control change events
        histogram_control.set_callback(self._handle_histogram_control_change)

        self._root_window.withdraw()

    def _handle_histogram_control_change(self, *args):
        # hex window is not visible
        if not self._is_visible:
            return

        # show hex dump or leave view alone
        if self._histogram_control.is_valid_cursor:
            self._set_view()

    def _set_view(self):
        # read page of media bytes starting at offset else warn and clear
        block_hash_offset = self._histogram_control.cursor_offset
        if block_hash_offset < 0:
            block_hash_offset = 0
        error_message, buf = read_media_bytes(
                                     self._data_manager.media_filename,
                                     block_hash_offset,
                                     self.BUFSIZE)
        if (error_message):
            ErrorWindow(self._root_window, "Open Error", error_message)
            self._clear_view()
            raise RuntimeError("bad: %s" % error_message)
            return

        # calculate the MD5 from the block of data in buf
        m = hashlib.md5()
        m.update(buf[:self._data_manager.hash_block_size])
        if len(buf) < self._data_manager.hash_block_size:
            # zero-extend the short block
            m.update(bytearray(self._data_manager.hash_block_size - len(buf)))
        block_hash = m.hexdigest()

        # generate annotation text about the selection
        text = ""
        is_in = block_hash in self._data_manager.hashes
        if is_in:

            # ignore and highlight status for hash
            if block_hash in self._data_manager.ignored_hashes:
                text += "hash ignored, "
            if block_hash in self._data_manager.highlighted_hashes:
                text += "hash highlighted, "

            # set ignore and highlight status for blocks matching this hash
            source_hashes = \
                    self._data_manager.hashes[block_hash]["source_hashes"]
            if len(self._data_manager.ignored_sources.intersection(
                                                              source_hashes)):
                text += "source ignored, "
            if len(self._data_manager.highlighted_sources.intersection(
                                                              source_hashes)):
                text += "source highlighted, "

            # also indicate matched identified data
            text += "hash matched"
        else:
            # indicate not matched identified data
            text += "hash not matched"

        # set annotation text
        self._annotation_label["text"] = text

        # set MD5 label
        self._md5_label["text"]='MD5: %s' % block_hash

        # set hex table
        self._media_hex_table.set_view(block_hash_offset, buf, is_in)

    def _clear_view(self):

        # clear annotation text
        self._annotation_label["text"] = "Status: No selection."

        # clear MD5 label
        self._md5_label["text"]='MD5: No selection.'

        # clear hex table
        self._media_hex_table.clear_view()

    def show(self):
        self._is_visible = True
        self._root_window.deiconify()
        self._root_window.lift()
        self._handle_histogram_control_change()

    def _hide(self):
        self._is_visible = False
        self._root_window.withdraw()

