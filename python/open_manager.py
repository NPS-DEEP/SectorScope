import identified_data
import filters
from show_error import ShowError
try:
    import tkinter
    import tkinter.filedialog as fd
except ImportError:
    import Tkinter as tkinter
    import tkFileDialog as fd

class OpenManager():
    """Opens a bulk_extractor directory, sets data, and fires events.
 
    Attributes:
      frame(Frame): The containing frame for this view.
      active_be_dir(str): The be_dir currently open, or "".
    """

    def __init__(self, master, identified_data, filters, offset_selection,
                                                         range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
        """

        # local references
        self._master = master
        self._identified_data = identified_data
        self._filters = filters
        self._offset_selection = offset_selection
        self._range_selection = range_selection

        # state
        active_be_dir = identified_data.be_dir

    """Open be_dir or if not be_dir open be_dir from chooser."""
    def open_be_dir(self, be_dir):
        if not be_dir:
            # get be_dir from chooser
            be_dir = fd.askdirectory(
                     title="Open bulk_extractor directory",
                     mustexist=True, initialdir=self._identified_data.be_dir)

        if not be_dir:
            # user did not choose, so abort
            return

        # read be_dir else show error window
        try:
            self._identified_data.read(be_dir)

        except Exception as e:
            ShowError(self._master, "Open Error", e)
            return

        # clear any filter settings
        self._filters.clear()
        self._filters.fire_change()

        # clear any byte offset selection
        self._offset_selection.clear()

        # clear any byte range selection
        self._range_selection.clear()

