import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from be_open_window import BEOpenWindow
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow

class OpenBEDir():
    """Opens a bulk_extractor directory, sets data, and fires events.
 
    Attributes:
      frame(Frame): The containing frame for this view.
      active_be_dir(str): The be_dir currently open, or "".
    """

    def __init__(self, master, identified_data, filters,
                 byte_offset_selection_trace_var):
        """Args:
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          byte_offset_selection_trace_var(tkinter Var): Variable to
            communicate selection change.
        """

        # local references
        self._master = master
        self._identified_data = identified_data
        self._filters = filters
        self._byte_offset_selection_trace_var = byte_offset_selection_trace_var

    def open(self):
    """Open be_dir from file chooser."""

    def open(self, be_dir):
    """Open be_dir and set active_be_dir else only modally report error."""

