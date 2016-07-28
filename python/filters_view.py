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

        # Ignore frame
        ignore_frame = tkinter.LabelFrame(highlight_and_ignore_frame,
                         text="Ignore", bg=colors.BACKGROUND, padx=4, pady=4)
        ignore_frame.pack(side=tkinter.LEFT, anchor="n")

        # ignore max same hashes text entry
        ignore_max_hashes_frame = tkinter.Frame(ignore_frame,
                                                bg=colors.BACKGROUND)
        ignore_max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(ignore_max_hashes_frame,
                      text="Max Duplicate Hashes:", padx=0, pady=0,
                      bg=colors.BACKGROUND).pack( side=tkinter.LEFT, anchor="w")
        self._ignore_max_hashes_entry = tkinter.Entry(ignore_max_hashes_frame,
                                                               width=6)
        self._ignore_max_hashes_entry.insert(0, "None")
        self._ignore_max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")

        # bind actions for ignore max hashes text entry
        self._ignore_max_hashes_entry.bind('<Return>',
                           self._handle_ignore_max_hashes_selection, add='+')
        self._ignore_max_hashes_entry.bind('<FocusOut>',
                           self._handle_ignore_max_hashes_selection, add='+')

        # ignore flagged blocks checkbutton
        self._ignore_flagged_blocks_checkbutton = tkinter.Checkbutton(
                        ignore_frame, text="Auto-filter",
                        variable=self._ignore_flagged_blocks_trace_var,
                        bd=0,
                        bg=colors.BACKGROUND,
                        activebackground=colors.ACTIVEBACKGROUND,
                        pady=4, highlightthickness=0)
        self._ignore_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                                 anchor="w")
        Tooltip(self._ignore_flagged_blocks_checkbutton,
                                         "Ignore flagged blocks")

        # bind actions for ignore_flagged_blocks checkbutton
        self._ignore_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_ignore_flagged_blocks_selection)

        # ignore buttons

        # ignore hashes in range
        self._ignore_hashes_in_range_icon = tkinter.PhotoImage(
                                 file=icon_path("ignore_hashes_in_range"))
        self._ignore_hashes_in_range_button = tkinter.Button(ignore_frame,
                           image=self._ignore_hashes_in_range_icon,
                           text="H",
                           compound="left", padx=4, pady=0,
                           command=self._handle_ignore_hashes_in_range,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._ignore_hashes_in_range_button.pack(side=tkinter.LEFT)
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
        self._ignore_sources_with_hashes_in_range_button.pack(side=tkinter.LEFT)
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
        self._clear_ignored_hashes_button.pack(side=tkinter.LEFT)
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
        self._clear_ignored_sources_button.pack(side=tkinter.LEFT)
        Tooltip(self._clear_ignored_sources_button, "Clear all ignored sources")

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

        # ignore max hashes
        self._set_ignore_max_hashes_entry(self._data_manager.ignore_max_hashes)

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

    def _set_ignore_max_hashes_entry(self, ignore_max_hashes):
        self._ignore_max_hashes_entry.delete(0, tkinter.END)
        if ignore_max_hashes == 0:
            self._ignore_max_hashes_entry.insert(0, "None")
        else:
            self._ignore_max_hashes_entry.insert(0, "%s" % ignore_max_hashes)

    def _handle_ignore_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            ignore_max_hashes = int(self._ignore_max_hashes_entry.get())
        except ValueError:
            ignore_max_hashes = 0

        # set entry to make sure it looks nice
        self._set_ignore_max_hashes_entry(ignore_max_hashes)

        # accept if change is from the user
        if not self._is_handle_filter_change:

            # drop focus so entry visually looks accepted
            # by giving focus to something that doesn't need or show it
            self.frame.focus()

            # ignore if no change
            if ignore_max_hashes == self._data_manager.ignore_max_hashes:
                return

            self._data_manager.ignore_max_hashes = ignore_max_hashes
            self._data_manager.fire_filter_change()

    def _handle_ignore_flagged_blocks_selection(self, *args):

        # accept if change is from the user
        if not self._is_handle_filter_change:
            # make the change
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

