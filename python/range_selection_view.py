from colors import background, activebackground
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from histogram_bar import HistogramBar
from image_hex_window import ImageHexWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class RangeSelectionView():
    """The range selection view including title, range values, and
    button controls.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
        """

        # data variables
        self._filters = filters
        self._range_selection = range_selection

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # title
        tkinter.Label(self.frame, text="Range Selection", bg=background).pack(
                                               side=tkinter.TOP, pady=(0,4))

        # range from
        self._from_label = tkinter.Label(self.frame, anchor="w", width=38,
                                                             bg=background)
        self._from_label.pack(side=tkinter.TOP, anchor="w")

        # range to
        self._to_label = tkinter.Label(self.frame, bg=background)
        self._to_label.pack(side=tkinter.TOP, anchor="w")

        # MD5 offset label
        self._md5_offset_label = tkinter.Label(self.frame, bg=background)
        self._md5_offset_label .pack(side=tkinter.TOP, anchor="w")

        # MD5 label
        self._md5_label = tkinter.Label(self.frame, anchor="w", width=40,
                                                           bg=background)
        self._md5_label.pack(side=tkinter.TOP, anchor="w", fill=tkinter.X)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set to basic initial state
        self._handle_range_selection_change()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # set labels and buttons based on range values

            # from
            self._from_label["text"]='From: %s' % offset_string(
                                          self._range_selection.start_offset)

            # to
            self._to_label["text"]='To: %s' % offset_string(
                                          self._range_selection.stop_offset)

            # MD5 offset
            self._md5_offset_label["text"]='MD5 offset: %s' % offset_string(
                                    self._range_selection.block_hash_offset)

            # MD5
            self._md5_label["text"]='MD5: %s' % self._range_selection.block_hash

        else:
            # set labels and buttons to unselected state
            self._from_label["text"]='From: Range not selected'
            self._to_label["text"]='To: Range not selected'
            self._md5_offset_label["text"]='MD5 offset: Range not selected'
            self._md5_label["text"]='MD5: Range not selected'

