import tkinter 
from collections import defaultdict
from scrolled_text import ScrolledText
from icon_path import icon_path
from tooltip import Tooltip
from sources_table import SourcesTable

class SourcesView():
    """Presents the view for the list of all matched sources.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): The filters that controll the view.
        """

        # colors
        self.LEGEND_FILTERED = "#006633"
        self.LEGEND_UNFILTERED = "#990000"

        # variables
        self._identified_data = identified_data
        self._filters = filters

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the title
        tkinter.Label(self.frame, text='All Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # add the select all and clear all buttons
        select_clear_frame = tkinter.Frame(self.frame)
        select_clear_frame.pack(pady=(0,4))

        # clear button
        self._clear_all_icon = tkinter.PhotoImage(file=icon_path("clear_all"))
        clear_all_button = tkinter.Button(select_clear_frame,
                       image=self._clear_all_icon,
                       command=self._handle_clear_all_sources)
        clear_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_all_button, "Do not filter any sources")

        # select button
        self._select_all_icon = tkinter.PhotoImage(file=icon_path("select_all"))
        select_all_button = tkinter.Button(select_clear_frame,
                       image=self._select_all_icon,
                       command=self._handle_set_all_sources)
        select_all_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(select_all_button, "Filter all sources")

        # the sources table
        self._sources_table = SourcesTable(self.frame, identified_data, filters,
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


    def _handle_clear_all_sources(self, *args):
        # clear filtered sources and signal change
        self._filters.filtered_sources.clear()
        self._filters.fire_change()

    def _handle_set_all_sources(self, *args):
        # set filtered sources and signal change
        self._filters.filtered_sources.clear()
        for source_id in self._identified_data.source_details:
            self._filters.filtered_sources.add(source_id)
        self._filters.fire_change()

