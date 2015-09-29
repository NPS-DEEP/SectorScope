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

    def __init__(self, master, identified_data, highlights):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          highlights(Highlights): The highlights that controll the view.
        """

        # variables
        self._identified_data = identified_data
        self._highlights = highlights

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # add the title
        tkinter.Label(self.frame, text='All Sources', bg=background).pack(
                                                             side=tkinter.TOP)

        # the sources table
        self._sources_table = SourcesTable(self.frame, identified_data,
                                                        highlights,
                                                        width=500, height=500)
        self._sources_table.frame.pack(side=tkinter.TOP, anchor="w")

        # register to receive identified data change events
        identified_data.set_callback(self._handle_identified_data_change)

    def _handle_identified_data_change(self, *args):
        # show all the source IDs
        source_id_set = set()
        for source_id, _ in self._identified_data.source_details.items():
            source_id_set.add(source_id)
        self._sources_table.set_data(source_id_set)

