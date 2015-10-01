from colors import background, activebackground
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar
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

    def __init__(self, master, identified_data, filters, range_selection,
                                                        fit_range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
          fit_range_selection(FitRangeSelection): Signal to fit range.
        """

        # data variables
        self._identified_data = identified_data
        self._filters = filters
        self._range_selection = range_selection
        self._fit_range_selection = fit_range_selection

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

        # clear range
        self._clear_range_icon = tkinter.PhotoImage(
                                  file=icon_path("clear_range"))
        self._clear_range_button = tkinter.Button(button_frame,
                              image=self._clear_range_icon,
                              command=self._handle_clear_range,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._clear_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_range_button, "Deselect range")

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set to basic initial state
        self._handle_range_selection_change()

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # set labels and buttons based on range values

            # range selected
            self._from_label["text"]='From: %s' % offset_string(
                                          self._range_selection.start_offset)
            self._to_label["text"]='To: %s' % offset_string(
                                          self._range_selection.stop_offset)

            self._fit_range_button.config(state=tkinter.NORMAL)
            self._clear_range_button.config(state=tkinter.NORMAL)

        else:
            # range not selected
            self._from_label["text"]='From: Range not selected'
            self._to_label["text"]='To: Range not selected'

            self._fit_range_button.config(state=tkinter.DISABLED)
            self._clear_range_button.config(state=tkinter.DISABLED)

    def _handle_clear_range(self):
        # clear range
        self._range_selection.clear()

