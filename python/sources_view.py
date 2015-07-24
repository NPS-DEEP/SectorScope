import tkinter 
from scrolled_canvas import ScrolledCanvas
from collections import defaultdict

class SourcesView():
    """Manages the view for the list of matched sources.

    Attributes:
      frame(Frame): the containing frame for this view.

      _checkbuttons(dict<checkbutton>): Source checkbuttons indexed by
        source_id.
      _checkbutton_state_vars(dict<BooleanVar>): Change signals to recalculate
        source selections.
    """

    def __init__(self, master, identified_data, filters):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): All data related to the block
            hash scan.
          filters(Filters): the filters that controll the view.
        """

        # variables
        self._identified_data = identified_data
        self._filters = filters
        self._is_changing = False

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # add the header text
        tkinter.Label(self.frame, text='Matched Sources') \
                                            .pack(side=tkinter.TOP)

        # add the select all and clear all buttons
        select_clear_frame = tkinter.Frame(self.frame)
        select_clear_frame.pack()
        tkinter.Button(select_clear_frame, text="Clear All",
                       command=self._handle_clear_all_checkbuttons).pack(
                                              side=tkinter.LEFT, padx=8)
        tkinter.Button(select_clear_frame, text="Set All",
                       command=self._handle_set_all_checkbuttons).pack(
                                              side=tkinter.LEFT, padx=8)

        # add the column titles
        tkinter.Label(self.frame, text='ID, %Match, #Match, Size, Repository, File') \
                                            .pack(side=tkinter.TOP, anchor="w")

        # make the frame to hold the canvas
        canvas_frame = tkinter.Frame(self.frame, bd=1, relief=tkinter.SUNKEN)
        canvas_frame.pack()

        # add the sources frame to contain the scrollable source list
        SOURCE_PIXEL_HEIGHT = 20
        frame_height = len(identified_data.source_details) * \
                                 SOURCE_PIXEL_HEIGHT + SOURCE_PIXEL_HEIGHT
        sources_canvas = ScrolledCanvas(canvas_frame,
                              canvas_width=400, canvas_height=800,
                              frame_width=800, frame_height=frame_height)
        sources_frame = sources_canvas.scrolled_frame

        # add the source checkbuttons and their checkbutton_states
        self._checkbuttons = dict()
        self._checkbutton_state_vars = dict()
        for source_id in identified_data.source_details:
            self._checkbutton_state_vars[source_id] = tkinter.BooleanVar()
            self._checkbutton_state_vars[source_id].trace_variable('w',
                                          self._handle_checkbutton_selection)
            self._checkbuttons[source_id] = tkinter.Checkbutton(
                            sources_frame,
                            variable = self._checkbutton_state_vars[source_id])
            self._checkbuttons[source_id].pack(side=tkinter.TOP, anchor="w")

        # fill out the source view
        self._fill_source_view()

        # register to receive filter change events
        filters.set_callback(self._handle_filter_change)

    def _fill_source_view(self):

        # optimization: make local references to filter variables
        max_hashes = self._filters.max_hashes
        filter_flagged_blocks = self._filters.filter_flagged_blocks
        filtered_sources = self._filters.filtered_sources
        filtered_hashes = self._filters.filtered_hashes

        # sources_offsets = dict<source ID, set<source offset int>>
        sources_offsets = defaultdict(set)

        # find each offset of each sector that is not filtered out
        for block_hash, sources in self._identified_data.hashes.items():

            # count exceeds max_hashes
            if max_hashes != 0 and len(sources) > max_hashes:
                continue

            # hash is filtered
            if block_hash in filtered_hashes:
                filter_count = len(sources)
                continue

            # a source is flagged or a source is marked
            for source in sources:
                if filter_flagged_blocks and "label" in source:
                    # source has a label flag
                    continue
                if source["source_id"] in filtered_sources:
                    # the source itself is filtered
                    continue

                # set the offset for the source
                sources_offsets[source["source_id"]].add(source["file_offset"])

        # fill out text for each source checkbox
        for source_id, source in self._identified_data.source_details.items():

             # calculate percent of this source file found
             percent_found = len(sources_offsets[source_id]) / \
                             (int(source["filesize"] / 
                             self._identified_data.sector_size)) * \
                             100

             # Source ID, %match, #match, file size, repository name, filename
             self._checkbuttons[source_id].config(
                      text='%s, %.2f%%, %d, %d, %s, %s' \
                                %(source_id,
                                  percent_found,
                                  len(sources_offsets[source_id]),
                                  source["filesize"],
                                  source["repository_name"],
                                  source["filename"]))
 
    def _handle_clear_all_checkbuttons(self, *args):
        # clear all the checkbuttons
        self._is_changing = True
        for state_var in self._checkbutton_state_vars.values():
            state_var.set(False)
        self._is_changing = False

        # clear filtered sources and signal change
        self._filters.filtered_sources.clear()
        self._filters.fire_change()

    def _handle_set_all_checkbuttons(self, *args):
        # set all the checkbuttons
        self._is_changing = True
        for state_var in self._checkbutton_state_vars.values():
            state_var.set(True)
        self._is_changing = False

        # set filtered sources and signal change
        self._filters.filtered_sources.clear()
        for source_id in self._identified_data.source_details:
            self._filters.filtered_sources.append(source_id)
        self._filters.fire_change()

    def _handle_checkbutton_selection(self, *args):
        # disregard event when changing everything
        if self._is_changing: return

        # build list of filtered sources
        self._filters.filtered_sources.clear()
        for source_id, state_var in self._checkbutton_state_vars.items():
            if state_var.get():
                self._filters.filtered_sources.append(source_id)

        # signal change
        self._filters.fire_change()

    def _handle_filter_change(self, *args):
        self._fill_source_view()

