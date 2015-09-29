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

    def __init__(self, master, identified_data, highlights, range_selection,
                                                        fit_range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          highlights(Highlights): Highlights that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
          fit_range_selection(FitRangeSelection): Signal to fit range.
        """

        # data variables
        self._identified_data = identified_data
        self._highlights = highlights
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

        # highlight sources in range
        self._highlight_sources_in_range_icon = tkinter.PhotoImage(
                                  file=icon_path("highlight_range"))
        self._highlight_sources_in_range_button = tkinter.Button(button_frame,
                              image=self._highlight_sources_in_range_icon,
                              command=self._handle_highlight_sources_in_range,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._highlight_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._highlight_sources_in_range_button,
                                               "Highlight sources in range")

        # highlight all but sources in range
        self._highlight_all_but_sources_in_range_icon = tkinter.PhotoImage(
                          file=icon_path("highlight_all_but_range"))
        self._highlight_all_but_sources_in_range_button = tkinter.Button(
                      button_frame,
                      image=self._highlight_all_but_sources_in_range_icon,
                      command=self._handle_highlight_all_but_sources_in_range,
                      bg=background, activebackground=activebackground,
                      highlightthickness=0)
        self._highlight_all_but_sources_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._highlight_all_but_sources_in_range_button,
                          "Highlight all but sources in range")

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
            self._highlight_sources_in_range_button.config(state=tkinter.NORMAL)
            self._highlight_all_but_sources_in_range_button.config(
                                                        state=tkinter.NORMAL)
            self._clear_range_button.config(state=tkinter.NORMAL)

        else:
            # range not selected
            self._from_label["text"]='From: Range not selected'
            self._to_label["text"]='To: Range not selected'

            self._fit_range_button.config(state=tkinter.DISABLED)
            self._highlight_sources_in_range_button.config(
                                                       state=tkinter.DISABLED)
            self._highlight_all_but_sources_in_range_button.config(
                                                       state=tkinter.DISABLED)
            self._clear_range_button.config(state=tkinter.DISABLED)

    def _handle_highlight_sources_in_range(self):
        # clear existing highlighted sources
        self._highlights.highlighted_sources.clear()

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and highlight variables
        hashes = self._identified_data.hashes
        highlighted_sources = self._highlights.highlighted_sources
        
        # highlight sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so highlight its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # highlight each source associated with this hash
                for source in sources:
                    highlighted_sources.add(source["source_id"])

        # fire highlight change
        self._highlights.fire_change()

    def _handle_highlight_all_but_sources_in_range(self):
        # start by highlighting all sources
        for source_id, _ in self._identified_data.source_details.items():
            self._highlights.highlighted_sources.add(source_id)

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and highlight variables
        hashes = self._identified_data.hashes
        highlighted_sources = self._highlights.highlighted_sources
        
        # unhighlight sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so highlight its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # unhighlight each source associated with this hash
                for source in sources:
                    highlighted_sources.discard(source["source_id"])

        # fire highlight change
        self._highlights.fire_change()

    def _handle_clear_range(self):
        # clear range
        self._range_selection.clear()

