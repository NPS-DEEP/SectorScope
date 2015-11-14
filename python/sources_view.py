import colors
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

    def __init__(self, master, data_manager, histogram_control):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages project data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
          """

        # variables
        self._data_manager = data_manager

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # add the title
        tkinter.Label(self.frame, text='Sources', bg=colors.BACKGROUND).pack(
                                                             side=tkinter.TOP)

        # the sources table
        self._sources_table = SourcesTable(self.frame, data_manager,
                                     histogram_control, width=500, height=500)
        self._sources_table.frame.pack(side=tkinter.TOP, anchor="w")

