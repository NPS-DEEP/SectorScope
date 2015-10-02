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

    def __init__(self, master, identified_data, filters,
                                   range_selection, fit_range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
          fit_range_selection(FitRangeSelection): Signal to fit range.
        """

        # data variables
        self._filters = filters
        self._range_selection = range_selection
        self._fit_range_selection = fit_range_selection

        # the image hex window that the show hex view button can show
        self._image_hex_window = ImageHexWindow(master, identified_data,
                                                  filters, range_selection)

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

        # button frame
        button_frame = tkinter.Frame(self.frame)
        button_frame.pack(side=tkinter.TOP)

        # zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(button_frame,
                              image=self._fit_range_icon,
                              command=self._fit_range_selection.fire_change,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._fit_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._fit_range_button, "Zoom to range")

        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        self._show_hex_view_button = tkinter.Button(button_frame,
                              image=self._show_hex_view_icon,
                              command=self._image_hex_window.show,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._show_hex_view_button.pack(side=tkinter.LEFT)
        Tooltip(self._show_hex_view_button, "Show hex view of selection")

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

            # fit range button
            self._fit_range_button.config(state=tkinter.NORMAL)

            # hex view button
            self._show_hex_view_button.config(state=tkinter.NORMAL)

        else:
            # set labels and buttons to unselected state
            self._from_label["text"]='From: Range not selected'
            self._to_label["text"]='To: Range not selected'
            self._md5_offset_label["text"]='MD5 offset: Range not selected'
            self._md5_label["text"]='MD5: Range not selected'

            self._fit_range_button.config(state=tkinter.DISABLED)
            self._show_hex_view_button.config(state=tkinter.DISABLED)

