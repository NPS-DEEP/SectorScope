from colors import background
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip
from sources_table import SourcesTable
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class SourcesView():
    """Presents the view for the list of all matched sources.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, offset_selection,
                                       range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
         """

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # add the title
        tkinter.Label(self.frame, text='Sources', bg=background).pack(
                                                             side=tkinter.TOP)

        # the sources table
        self._sources_table = SourcesTable(self.frame, identified_data,
                                         filters, offset_selection,
                                         range_selection,
                                         width=500, height=500)
        self._sources_table.frame.pack(side=tkinter.TOP, anchor="w")

