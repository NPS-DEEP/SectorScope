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

        # add the frame to contain the image hex table
        image_hex_table = ImageHexTable(self._root_window, identified_data,
                                       range_selection, width=88, height=32)
        image_hex_table.frame.pack(side=tkinter.TOP, anchor="w")

        # register to receive filter change events
        filters.set_callback(self._handle_annotation)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_annotation)

        self._root_window.withdraw()

    def _handle_annotation(self, *args):
        # put in annotation about the selection
        text = ""
        if self._range_selection.is_selected:
            block_hash = self._range_selection.block_hash
            if self._range_selection.block_hash_is_in:
                # ignore and highlight status for hash
                if block_hash in self._filters.ignored_hashes:
                    text += "hash ignored, "
                if block_hash in self._filters.highlighted_hashes:
                    text += "hash highlighted, "

                # ignore and highlight status for sectors matching hash
                # get sources associated with this hash
                sources = self._identified_data.hashes[block_hash]

                # get status for each source associated with this hash
                source_ignored = False
                source_highlighted = False
                for source in sources:
                    source_id = source["source_id"]
                    if source_id in self._filters.ignored_sources:
                        source_ignored = True
                    if source_id in self._filters.highlighted_sources:
                        source_highlighted = True
                if source_ignored:
                    text += "source ignored, "
                if source_highlighted:
                    text += "source highlighted, "
                text += "hash matched"
            else:
                text += "hash not matched"
        else:
            text = "No selection."
        self._annotation_label["text"] = text

    def show(self):
        self._root_window.deiconify()

    def _hide(self):
        self._root_window.withdraw()

