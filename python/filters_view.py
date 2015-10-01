from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow
from colors import background, activebackground
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class FiltersView():
    """Provides filter controls for ignored and highlighted hashes and sources.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, filters, offset_selection, range_selection):
        """Args:
          master(a UI container): Parent.
          filters(Filters): Filters for hashes and sources.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
         """

        # state to prevent infinite filter change loop
        self._is_handle_filter_change = False

        # UI state
        self._ignore_flagged_blocks_trace_var = tkinter.IntVar()

        # filters
        self._filters = filters

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # title
        tkinter.Label(self.frame, text="Filters", bg=background).pack(
                                               side=tkinter.TOP, pady=(0,4))

        # Ignore frame
        ignore_frame = tkinter.LabelFrame(self.frame, text="Ignore",
                                             bg=background, padx=4, pady=4)
        ignore_frame.pack(side=tkinter.TOP)

        # ignore max same hashes text entry
        ignore_max_hashes_frame = tkinter.Frame(ignore_frame, bg=background)
        ignore_max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(ignore_max_hashes_frame,
                      text="Max Same Hashes:", padx=0, pady=0,
                      bg=background).pack( side=tkinter.LEFT, anchor="w")
        self.ignore_max_hashes_entry = tkinter.Entry(ignore_max_hashes_frame,
                                                               width=6)
        self.ignore_max_hashes_entry.insert(0, "None")
        self.ignore_max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")

        # bind actions for ignore max hashes text entry
        self.ignore_max_hashes_entry.bind('<Return>',
                           self._handle_ignore_max_hashes_selection, add='+')
        self.ignore_max_hashes_entry.bind('<FocusOut>',
                           self._handle_ignore_max_hashes_selection, add='+')

        # ignore flagged blocks checkbutton
        self.ignore_flagged_blocks_checkbutton = tkinter.Checkbutton(
                        ignore_frame, text="Flagged Blocks",
                        variable=self._ignore_flagged_blocks_trace_var,
                        bd=0, bg=background, activebackground=activebackground,
                        pady=4, highlightthickness=0)
        self.ignore_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                                 anchor="w")

        # bind actions for ignore_flagged_blocks checkbutton
        self._ignore_flagged_blocks_trace_var.set(filters.ignore_flagged_blocks)
        self._ignore_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_ignore_flagged_blocks_selection)

        # ignore buttons

        # ignore hashes in range
        self._ignore_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_hashes_in_range"))
        button = tkinter.Button(ignore_frame,
                           image=self._ignore_hashes_in_range_icon,
                           text="Hashes in range",
                           compound="left", padx=4, pady=0,
                           command=self._handle_ignore_hashes_in_range,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore hashes in range selection")

        # ignore selected hash
        self._ignore_selected_hash_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_selected_hash"))
        button = tkinter.Button(ignore_frame,
                           image=self._ignore_selected_hash_icon,
                           text="Selected hash",
                           compound="left", padx=4, pady=0,
                           command=self._handle_ignore_selected_hash,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore hash at offset selection")

        # ignore sources with hashes in range
        self._ignore_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("ignore_sources_with_hashes_in_range"))
        button = tkinter.Button(ignore_frame,
                   image=self._ignore_sources_with_hashes_in_range_icon,
                   text="Hashes in range",
                   compound="left", padx=4, pady=0,
                   command=self._handle_ignore_sources_with_hashes_in_range,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore sources with hashes in range selection")

        # ignore sources with selected hash
        self._ignore_sources_with_selected_hash_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_sources_with_selected_hash"))
        button = tkinter.Button(ignore_frame,
                   image=self._ignore_sources_with_selected_hash_icon,
                   text="Sources with selected hash",
                   compound="left", padx=4, pady=0,
                   command=self._handle_ignore_sources_with_selected_hash,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore sources containing hash at offset selection")

        # clear ignored hashes
        self._clear_ignored_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_hashes"))
        button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_hashes_icon,
                   text="Clear ignored hashes",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_ignored_hashes,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Clear all ignored hashes")

        # clear ignore sources
        self._clear_ignored_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_sources"))
        button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_sources_icon,
                   text="Clear ignored sources",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_ignored_sources,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Clear all ignored sources")

        # Highlight frame
        highlight_frame = tkinter.LabelFrame(self.frame, text="Highlight",
                                             bg=background, padx=4, pady=4)
        highlight_frame.pack(side=tkinter.TOP, anchor="w")

        # highlight buttons

        # highlight hashes in range
        self._highlight_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("highlight_hashes_in_range"))
        button = tkinter.Button(highlight_frame,
                           image=self._highlight_hashes_in_range_icon,
                           text="Hashes in range",
                           compound="left", padx=4, pady=0,
                           command=self._handle_highlight_hashes_in_range,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore hashes in range selection")

        # highlight selected hash
        self._highlight_selected_hash_icon = tkinter.PhotoImage(
                                 file=icon_path("highlight_selected_hash"))
        button = tkinter.Button(highlight_frame,
                           image=self._highlight_selected_hash_icon,
                           text="Selected hash",
                           compound="left", padx=4, pady=0,
                           command=self._handle_highlight_selected_hash,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore hash at offset selection")

        # highlight sources with hashes in range
        self._highlight_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("highlight_sources_with_hashes_in_range"))
        button = tkinter.Button(highlight_frame,
                   image=self._highlight_sources_with_hashes_in_range_icon,
                   text="Hashes in range",
                   compound="left", padx=4, pady=0,
                   command=self._handle_highlight_sources_with_hashes_in_range,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore sources with hashes in range selection")

        # highlight sources with selected hash
        self._highlight_sources_with_selected_hash_icon = tkinter.PhotoImage(
                       file=icon_path("highlight_sources_with_selected_hash"))
        button = tkinter.Button(highlight_frame,
                   image=self._highlight_sources_with_selected_hash_icon,
                   text="Sources with selected hash",
                   compound="left", padx=4, pady=0,
                   command=self._handle_highlight_sources_with_selected_hash,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Ignore sources containing hash at offset selection")

        # clear highlighted hashes
        self._clear_highlighted_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlightd_hashes"))
        button = tkinter.Button(highlight_frame,
                   image=self._clear_highlightd_hashes_icon,
                   text="Clear highlighted hashes",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_highlightd_hashes,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Clear all highlighted hashes")

        # clear highlight sources
        self._clear_highlightd_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlightd_sources"))
        button = tkinter.Button(highlight_frame,
                   image=self._clear_highlightd_sources_icon,
                   text="Clear highlighted sources",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_highlightd_sources,
                   bg=background, activebackground=activebackground,
                   highlightthickness=0)
        button.pack(side=tkinter.LEFT)
        Tooltip(button, "Clear all highlighted sources")

        # register to receive highlight change events
        filters.set_callback(self._handle_highlight_change)

        # register to receive offset selection change events
        offset_selection.set_callback(self._handle_offset_selection_change)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)



#        # set initial state
#        self._handle_filter_change()
#        self._handle_offset_selection_change()




    def _handle_offset_selection_change(self, *args):

        # set selection labels and button states
        if self._offset_selection.offset == -1:
            # clear
            self._show_hex_view_button.config(state=tkinter.DISABLED)
            self._clear_offset_selection_button.config(
                                              state=tkinter.DISABLED)

        else:
            # set to selection
            self._show_hex_view_button.config(state=tkinter.NORMAL)
            self._clear_offset_selection_button.config(
                                              state=tkinter.NORMAL)

        # set filter button states
        self._set_filter_button_states()

 







    def _set_filter_button_states(self):
        # disable both if there is no active selection
        if self._offset_selection.offset == -1:
            self._ignore_hash_button.config(state=tkinter.DISABLED)
            self._unignore_hash_button.config(state=tkinter.DISABLED)
            self._highlight_hash_button.config(state=tkinter.DISABLED)
            self._unhighlight_hash_button.config(state=tkinter.DISABLED)
            return

        # reference to selected hash
        selected_hash = self._offset_selection.block_hash

        # set enabled state of the ignore hash button
        if selected_hash not in self._filters.ignored_hashes and \
                           selected_hash in self._identified_data.hashes:
            self._ignore_hash_button.config(state=tkinter.NORMAL)
        else:
            self._ignore_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the unignore hash button
        if selected_hash in self._filters.ignored_hashes:
            self._unignore_hash_button.config(state=tkinter.NORMAL)
        else:
            self._unignore_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the highlight hash button
        if selected_hash not in self._filters.highlighted_hashes and \
                           selected_hash in self._identified_data.hashes:
            self._highlight_hash_button.config(state=tkinter.NORMAL)
        else:
            self._highlight_hash_button.config(state=tkinter.DISABLED)

        # set enabled state of the unhighlight hash button
        if selected_hash in self._filters.highlighted_hashes:
            self._unhighlight_hash_button.config(state=tkinter.NORMAL)
        else:
            self._unhighlight_hash_button.config(state=tkinter.DISABLED)













    def _handle_highlight_sources_in_range(self):
        # clear existing highlighted sources
        self._filters.highlighted_sources.clear()

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and highlight variables
        hashes = self._identified_data.hashes
        highlighted_sources = self._filters.highlighted_sources
        
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
        self._filters.fire_change()

    def _handle_ignore_sources_in_range(self):
        # clear existing ignored sources
        self._filters.ignored_sources.clear()

        # get start_byte and stop_byte range
        start_byte = self._range_selection.start_offset
        stop_byte = self._range_selection.stop_offset

        # get local references to identified data and filter variables
        hashes = self._identified_data.hashes
        ignored_sources = self._filters.ignored_sources
        
        # ignore sources in range
        seen_hashes = set()
        for forensic_path, block_hash in \
                               self._identified_data.forensic_paths.items():
            offset = int(forensic_path)
            if offset >= start_byte and offset <= stop_byte:
                # hash is in range so ignore its sources
                if block_hash in seen_hashes:
                    # do not reprocess this hash
                    continue

                # remember this hash
                seen_hashes.add(block_hash)

                # get sources associated with this hash
                sources = hashes[block_hash]

                # ignore each source associated with this hash
                for source in sources:
                    ignored_sources.add(source["source_id"])

        # fire highlight change
        self._filters.fire_change()

    # this function is registered to and called by OffsetSelection
    def _handle_offset_selection_change(self, *args):
        print("TBD offset")

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        print("TBD range")
#        if self._range_selection.is_selected:
#            # set labels and buttons based on range values
#
#            # range selected
#            self._fit_range_button.config(state=tkinter.NORMAL)
#            self._highlight_sources_in_range_button.config(state=tkinter.NORMAL)
#            self._ignore_sources_in_range_button.config(state=tkinter.NORMAL)
#            self._clear_range_button.config(state=tkinter.NORMAL)

#        else:
#            # range not selected
#            self._fit_range_button.config(state=tkinter.DISABLED)
#            self._highlight_sources_in_range_button.config(
#                                                       state=tkinter.DISABLED)
#            self._ignore_sources_in_range_button.config(
#                                                       state=tkinter.DISABLED)
#            self._clear_range_button.config(state=tkinter.DISABLED)



    def _set_ignore_max_hashes_entry(self, ignore_max_hashes):
        self.ignore_max_hashes_entry.delete(0, tkinter.END)
        if ignore_max_hashes == 0:
            self.ignore_max_hashes_entry.insert(0, "None")
        else:
            self.ignore_max_hashes_entry.insert(0, "%s"%max_hashes)


    def _handle_ignore_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            ignore_max_hashes = int(self.ignore_max_hashes_entry.get())
        except ValueError:
            ignore_max_hashes = 0

        # set entry to make sure it looks nice
        self._set_ignore_max_hashes_entry(ignore_max_hashes)

        # fire if change is from the user
        if not self._is_handle_filter_change:

            # only set if ignore_max_hashes changes
            if ignore_max_hashes != self._filters.ignore_max_hashes:
                self._fiters.ignore_max_hashes = ignore_max_hashes
                self._filters.fire_change()

    def _handle_ignore_flagged_blocks_selection(self, *args):
        self._filters.ignore_flagged_blocks = \
                               self._ignore_flagged_blocks_trace_var.get()

        # fire if change is from the user
        if not self._is_handle_filter_change:
            self._filters.fire_change()

    def _handle_clear_highlighted_sources(self, *args):
        # clear highlighted sources and signal change
        self._filters.highlighted_sources.clear()
        self._filters.fire_change()

    def _handle_clear_highlighted_hashes(self, *args):
        # clear highlighted hashes and signal change
        self._filters.highlighted_hashes.clear()
        self._filters.fire_change()

    def _handle_clear_ignored_sources(self, *args):
        # clear ignored sources and signal change
        self._filters.ignored_sources.clear()
        self._filters.fire_change()

    def _handle_clear_ignored_hashes(self, *args):
        # clear ignored hashes and signal change
        self._filters.ignored_hashes.clear()
        self._filters.fire_change()

    def _handle_highlight_change(self, *args):
        self._is_handle_highlight_change = True
        self._set_ignore_max_hashes_entry(self._filters.ignore_max_hashes)
        self._ignore_flagged_blocks_trace_var.set(
                                   self._filters.ignore_flagged_blocks)
        self._is_handle_highlight_change = False

