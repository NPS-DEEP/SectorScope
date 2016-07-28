from icon_path import icon_path
from tooltip import Tooltip
import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class FiltersView():
    """Provides filter controls for ignored and highlighted hashes and sources.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, data_manager, histogram_control):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
         """

        self._data_manager = data_manager
        self._histogram_control = histogram_control

        # state to prevent infinite filter change loop
        self._is_handle_filter_change = False

        # UI state
        self._ignore_flagged_blocks_trace_var = tkinter.IntVar()

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # highlight and ignore frame
        highlight_and_ignore_frame = tkinter.Frame(self.frame,
                                                        bg=colors.BACKGROUND)
        highlight_and_ignore_frame.pack(side=tkinter.TOP, anchor="w")

        # Highlight frame
        highlight_frame = tkinter.LabelFrame(highlight_and_ignore_frame,
                      text="Highlight", bg=colors.BACKGROUND, padx=4, pady=4)
        highlight_frame.pack(side=tkinter.LEFT, anchor="n", padx=(0,4))

        # highlight buttons

        # highlight hashes in range
        self._highlight_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("highlight_hashes_in_range"))
        self._highlight_hashes_in_range_button = tkinter.Button(highlight_frame,
                           image=self._highlight_hashes_in_range_icon,
                           text="H",
                           compound="left", padx=4, pady=0,
                           command=self._handle_highlight_hashes_in_range,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._highlight_hashes_in_range_button.pack(side=tkinter.LEFT)
        Tooltip(self._highlight_hashes_in_range_button,
                                      "Highlight hashes in selected range")

        # highlight sources with hashes in range
        self._highlight_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("highlight_sources_with_hashes_in_range"))
        self._highlight_sources_with_hashes_in_range_button = tkinter.Button(
                   highlight_frame,
                   image=self._highlight_sources_with_hashes_in_range_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._handle_highlight_sources_with_hashes_in_range,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._highlight_sources_with_hashes_in_range_button.pack(
                                               side=tkinter.LEFT)
        Tooltip(self._highlight_sources_with_hashes_in_range_button,
                          "Highlight sources with hashes in selected range")

        # clear highlighted hashes
        self._clear_highlighted_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_hashes"))
        self._clear_highlighted_hashes_button = tkinter.Button(highlight_frame,
                   image=self._clear_highlighted_hashes_icon,
                   text="H",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_highlighted_hashes,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_highlighted_hashes_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_highlighted_hashes_button,
                                           "Clear all highlighted hashes")

        # clear highlighted sources
        self._clear_highlighted_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_sources"))
        self._clear_highlighted_sources_button = tkinter.Button(highlight_frame,
                   image=self._clear_highlighted_sources_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_highlighted_sources,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_highlighted_sources_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_highlighted_sources_button,
                                           "Clear all highlighted sources")

        # ignore frame
        ignore_frame = tkinter.LabelFrame(highlight_and_ignore_frame,
                         text="Ignore", bg=colors.BACKGROUND, padx=4, pady=4)

        # ignore hashes in range
        self._ignore_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_hashes_in_range"))
        self._ignore_hashes_in_range_button = tkinter.Button(
                   ignore_frame, image=self._ignore_hashes_in_range_icon,
                   text="H",
                   compound="left", padx=4, pady=0,
                   command=self._handle_ignore_hashes_in_range,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._ignore_hashes_in_range_button.grid(
                                        row=0, column=0, sticky=tkinter.W)
        Tooltip(self._ignore_hashes_in_range_button,
                                         "Ignore hashes in selected range")

        # ignore sources with hashes in range
        self._ignore_sources_with_hashes_in_range_icon = tkinter.PhotoImage(
                       file=icon_path("ignore_sources_with_hashes_in_range"))
        self._ignore_sources_with_hashes_in_range_button = tkinter.Button(
                   ignore_frame,
                   image=self._ignore_sources_with_hashes_in_range_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._handle_ignore_sources_with_hashes_in_range,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._ignore_sources_with_hashes_in_range_button.grid(
                                        row=0, column=1, sticky=tkinter.W)
        Tooltip(self._ignore_sources_with_hashes_in_range_button,
                             "Ignore sources with hashes in selected range")

        # clear ignored hashes
        self._clear_ignored_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_hashes"))
        self._clear_ignored_hashes_button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_hashes_icon,
                   text="H",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_ignored_hashes,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_ignored_hashes_button.grid(
                                        row=0, column=2, sticky=tkinter.W)
        Tooltip(self._clear_ignored_hashes_button, "Clear all ignored hashes")

        # clear ignored sources
        self._clear_ignored_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_ignored_sources"))
        self._clear_ignored_sources_button = tkinter.Button(ignore_frame,
                   image=self._clear_ignored_sources_icon,
                   text="S",
                   compound="left", padx=4, pady=0,
                   command=self._handle_clear_ignored_sources,
                   bg=colors.BACKGROUND,
                   activebackground=colors.ACTIVEBACKGROUND,
                   highlightthickness=0)
        self._clear_ignored_sources_button.grid(
                                        row=0, column=3, sticky=tkinter.W)
        Tooltip(self._clear_ignored_sources_button, "Clear all ignored sources")

        # ignore entropy below
        tkinter.Label(ignore_frame,
                      text="Entropy Below:", padx=0, pady=0,
                      bg=colors.BACKGROUND).grid(padx=(16,4),
                                        row=0, column=4, sticky=tkinter.E)
        self._ignore_entropy_below_entry = tkinter.Entry(ignore_frame, width=6)
        self._ignore_entropy_below_entry.insert(0, "None")
        self._ignore_entropy_below_entry.grid(
                                        row=0, column=5, sticky=tkinter.W)

        # bind actions for ignore max hashes text entry
        self._ignore_entropy_below_entry.bind('<Return>',
                           self._handle_selection_change, add='+')
        self._ignore_entropy_below_entry.bind('<FocusOut>',
                           self._handle_selection_change, add='+')

        # ignore entropy above
        tkinter.Label(ignore_frame,
                      text="Entropy Above:", padx=0, pady=0,
                      bg=colors.BACKGROUND).grid(padx=(16,4),
                                        row=1, column=4, sticky=tkinter.E)
        self._ignore_entropy_above_entry = tkinter.Entry(ignore_frame, width=6)
        self._ignore_entropy_above_entry.insert(0, "None")
        self._ignore_entropy_above_entry.grid(
                                        row=1, column=5, sticky=tkinter.W)

        # bind actions for ignore max hashes text entry
        self._ignore_entropy_above_entry.bind('<Return>',
                           self._handle_selection_change, add='+')
        self._ignore_entropy_above_entry.bind('<FocusOut>',
                           self._handle_selection_change, add='+')

        # ignore max same hashes text entry
        tkinter.Label(ignore_frame,
                      text="Max Duplicate Hashes:", padx=0, pady=0,
                      bg=colors.BACKGROUND).grid(padx=(16,4),
                                        row=0, column=6, sticky=tkinter.E)
        self._ignore_max_hashes_entry = tkinter.Entry(ignore_frame, width=6)
        self._ignore_max_hashes_entry.insert(0, "None")
        self._ignore_max_hashes_entry.grid(
                                        row=0, column=7, sticky=tkinter.W)

        # bind actions for ignore max hashes text entry
        self._ignore_max_hashes_entry.bind('<Return>',
                           self._handle_selection_change, add='+')
        self._ignore_max_hashes_entry.bind('<FocusOut>',
                           self._handle_selection_change, add='+')

        # ignore flagged blocks checkbutton auto-filter
        self._ignore_flagged_blocks_checkbutton = tkinter.Checkbutton(
                        ignore_frame, text="Auto-filter",
                        variable=self._ignore_flagged_blocks_trace_var,
                        bd=0,
                        bg=colors.BACKGROUND,
                        activebackground=colors.ACTIVEBACKGROUND,
                        pady=4, highlightthickness=0)
        self._ignore_flagged_blocks_checkbutton.grid(padx=(16,4),
                                        row=1, column=6, sticky=tkinter.W)
        Tooltip(self._ignore_flagged_blocks_checkbutton,
                                         "Ignore flagged blocks")

        # pack ignore_frame
        ignore_frame.pack(side=tkinter.TOP, anchor="w")

        # bind actions for ignore_flagged_blocks checkbutton auto-filter
        self._ignore_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_selection_change)

        # register to receive data manager change events
        data_manager.set_callback(self._handle_data_manager_change)

        # register to receive histogram control change events
        histogram_control.set_callback(self._handle_histogram_control_change)

        # set initial state
        self._handle_data_manager_change()
        self._handle_histogram_control_change()

    def _handle_data_manager_change(self, *args):
        # set state for ignore max hashes entry and ignore
        # flagged blocks trace var without causing a circular
        # handle_filter_change loop
        self._is_handle_filter_change = True

        # entropy below
        self._set_numeric_entry(self._ignore_entropy_below_entry,
                                self._data_manager.ignore_entropy_below)

        # entropy above
        self._set_numeric_entry(self._ignore_entropy_above_entry,
                                self._data_manager.ignore_entropy_above)

        # ignore max hashes
        self._set_numeric_entry(self._ignore_max_hashes_entry,
                                self._data_manager.ignore_max_hashes)

        # ignore flagged blocks
        self._ignore_flagged_blocks_trace_var.set(
                                   self._data_manager.ignore_flagged_blocks)

        # ignored hashes
        if len(self._data_manager.ignored_hashes):
            self._clear_ignored_hashes_button.config(state=tkinter.NORMAL)
        else:
            self._clear_ignored_hashes_button.config(state=tkinter.DISABLED)

        # ignored sources
        if len(self._data_manager.ignored_sources):
            self._clear_ignored_sources_button.config(state=tkinter.NORMAL)
        else:
            self._clear_ignored_sources_button.config(state=tkinter.DISABLED)

        # highlighted hashes
        if len(self._data_manager.highlighted_hashes):
            self._clear_highlighted_hashes_button.config(state=tkinter.NORMAL)
        else:
            self._clear_highlighted_hashes_button.config(state=tkinter.DISABLED)

        # highlighted sources
        if len(self._data_manager.highlighted_sources):
            self._clear_highlighted_sources_button.config(state=tkinter.NORMAL)
        else:
            self._clear_highlighted_sources_button.config(
                                                       state=tkinter.DISABLED)

        self._is_handle_filter_change = False

    def _handle_histogram_control_change(self, *args):
        if self._histogram_control.is_valid_range:
            state = tkinter.NORMAL
        else:
            state = tkinter.DISABLED
        self._ignore_hashes_in_range_button.config(state=state)
        self._ignore_sources_with_hashes_in_range_button.config(state=state)
        self._highlight_hashes_in_range_button.config(state=state)
        self._highlight_sources_with_hashes_in_range_button.config(state=state)

    def _set_numeric_entry(self, entry, value):
        entry.delete(0, tkinter.END)
        if value == 0:
            entry.insert(0, "None")
        else:
            entry.insert(0, "%s" % value)

    def _handle_selection_change(self, *_):
        # Note: entries take e and trace_variable takes *arg so use *_
        # change is one of: max hashes, entropy below, or entropy above
        # text or flagged blocks checkbox

        # entropy_below
        try:
            ignore_entropy_below = float(self._ignore_entropy_below_entry.get())
        except ValueError:
            ignore_entropy_below = 0
        self._set_numeric_entry(self._ignore_entropy_below_entry,
                                ignore_entropy_below)

        # entropy_above
        try:
            ignore_entropy_above = float(self._ignore_entropy_above_entry.get())
        except ValueError:
            ignore_entropy_above = 0
        self._set_numeric_entry(self._ignore_entropy_above_entry,
                                ignore_entropy_above)

        # max_hashes
        try:
            ignore_max_hashes = int(self._ignore_max_hashes_entry.get())
        except ValueError:
            ignore_max_hashes = 0
        self._set_numeric_entry(self._ignore_max_hashes_entry,
                                ignore_max_hashes)

        # done if change is from filter handler
        if self._is_handle_filter_change:
            return

        # done if user change is same
        if ignore_entropy_below == self._data_manager.ignore_entropy_below and \
           ignore_entropy_above == self._data_manager.ignore_entropy_above and \
           ignore_max_hashes == self._data_manager.ignore_max_hashes and \
           self._ignore_flagged_blocks_trace_var.get() == \
                                   self._data_manager.ignore_flagged_blocks:
            return

        # drop focus so entry visually looks accepted
        # by giving focus to something that doesn't need or show it
        self.frame.focus()

        # accept and forward user selection change event
        self._data_manager.ignore_entropy_below = ignore_entropy_below
        self._data_manager.ignore_entropy_above = ignore_entropy_above
        self._data_manager.ignore_max_hashes = ignore_max_hashes
        self._data_manager.ignore_flagged_blocks = \
                                self._ignore_flagged_blocks_trace_var.get()
        self._data_manager.fire_filter_change()

    # filter button handlers
    def _handle_highlight_hashes_in_range(self):
        self._data_manager.highlight_hashes_in_range(
                                       self._histogram_control.range_start,
                                       self._histogram_control.range_stop)
    def _handle_highlight_sources_with_hashes_in_range(self):
        self._data_manager.highlight_sources_with_hashes_in_range(
                                       self._histogram_control.range_start,
                                       self._histogram_control.range_stop)
    def _handle_clear_highlighted_hashes(self):
        self._data_manager.clear_highlighted_hashes()
    def _handle_clear_highlighted_sources(self):
        self._data_manager.clear_highlighted_sources()
    def _handle_ignore_hashes_in_range(self):
        self._data_manager.ignore_hashes_in_range(
                                       self._histogram_control.range_start,
                                       self._histogram_control.range_stop)
    def _handle_ignore_sources_with_hashes_in_range(self):
        self._data_manager.ignore_sources_with_hashes_in_range(
                                       self._histogram_control.range_start,
                                       self._histogram_control.range_stop)
    def _handle_clear_ignored_hashes(self):
        self._data_manager.clear_ignored_hashes()
    def _handle_clear_ignored_sources(self):
        self._data_manager.clear_ignored_sources()

