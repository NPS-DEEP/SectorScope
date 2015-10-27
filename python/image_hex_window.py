from image_hex_table import ImageHexTable
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ImageHexWindow():
    """Provides a window to show a hex dump of specified bytes of a
    media image.
    """
    def __init__(self, master, identified_data, filters, range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(OffsetSelection): The selected range.
        """
        # variables
        self._identified_data = identified_data
        self._filters = filters
        self._range_selection = range_selection

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

        # add the frame to contain the image hex table
        image_hex_table = ImageHexTable(self._root_window, identified_data,
                                       range_selection, width=88, height=32)
        image_hex_table.frame.pack(side=tkinter.TOP, anchor="w")

        # register to receive filter change events
        filters.set_callback(self._handle_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_change)

        self._root_window.withdraw()

    def _handle_change(self, *args):
        # generate annotation text about the selection
        text = ""
        if self._range_selection.is_selected:
            block_hash = self._range_selection.block_hash
            if self._range_selection.block_hash_is_in:
                # ignore and highlight status for hash
                if block_hash in self._filters.ignored_hashes:
                    text += "hash ignored, "
                if block_hash in self._filters.highlighted_hashes:
                    text += "hash highlighted, "

                # set ignore and highlight status for blocks matching this hash
                (_, source_id_set, _, _) = \
                                     self._identified_data.hashes[block_hash]
                if len(self._filters.ignored_sources.intersection(
                                                             source_id_set)):
                    text += "source ignored, "
                if len(self._filters.highlighted_sources.intersection(
                                                             source_id_set)):
                    text += "source highlighted, "

                # also indicate matched identified_data
                text += "hash matched"
            else:
                # indicate not matched identified_data
                text += "hash not matched"
        else:
            # no hash is selected
            text = "Status: No selection."

        # set annotation text
        self._annotation_label["text"] = text

        # set MD5
        if self._range_selection.is_selected:
            self._md5_label["text"]='MD5: %s' % self._range_selection.block_hash
        else:
            self._md5_label["text"]='MD5: No selection.'

    def show(self):
        self._root_window.deiconify()

    def _hide(self):
        self._root_window.withdraw()

