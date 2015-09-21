import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow

class HighlightsSummaryView():
    """Provides a highlight summary frame containing highlight controls.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, highlights):
        """Args:
          master(a UI container): Parent.
          highlights(Highlights): Highlights for hashes and sources.
        """

        # state to prevent infinite highlight change loop
        self._is_handle_highlight_change = False

        # UI state
        self._highlight_flagged_blocks_trace_var = tkinter.IntVar()

        # highlights
        self._highlights = highlights

        # make the containing frame
        self.frame = tkinter.Frame(master, padx=4, pady=4)

        # title
        tkinter.Label(self.frame, text="Highlights").pack(pady=(0,4))

        # max hashes text entry
        max_hashes_frame = tkinter.Frame(self.frame)
        max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(max_hashes_frame, text="Max Same Hashes:") \
                                        .pack(side=tkinter.LEFT, anchor="w")
        self.max_hashes_entry = tkinter.Entry(max_hashes_frame, width=6)
        self.max_hashes_entry.insert(0, "None")
        self.max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")

        # bind actions for max hashes text entry
        self.max_hashes_entry.bind('<Return>',
                                   self._handle_max_hashes_selection, add='+')
        self.max_hashes_entry.bind('<FocusOut>',
                                   self._handle_max_hashes_selection, add='+')

        # highlight_flagged_blocks checkbutton
        self.highlight_flagged_blocks_checkbutton = tkinter.Checkbutton(
                           self.frame, text="Highlight Flagged Blocks",
                           variable=self._highlight_flagged_blocks_trace_var,
                           bd=0,padx=2,pady=2)
        self.highlight_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                    anchor="w")

        # bind actions for highlight_flagged_blocks checkbutton
        self._highlight_flagged_blocks_trace_var.set(
                                         highlights.highlight_flagged_blocks)
        self._highlight_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_highlight_flagged_blocks_selection)

        buttons_frame = tkinter.Frame(self.frame)
        buttons_frame.pack(side=tkinter.TOP, anchor="w")

        # clear highlighted sources button
        self._clear_highlighted_sources_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_sources"))
        clear_highlighted_sources_button = tkinter.Button(buttons_frame,
                           image=self._clear_highlighted_sources_icon,
                           command=self._handle_clear_highlighted_sources)
        clear_highlighted_sources_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_highlighted_sources_button,
                                             "Clear all highlighted sources")

        # clear highlighted sources label
        tkinter.Label(buttons_frame, text="Sources"
                          ).pack(side=tkinter.LEFT, anchor="w", padx=(0,16))

        # clear highlighted hashes button
        self._clear_highlighted_hashes_icon = tkinter.PhotoImage(
                                 file=icon_path("clear_highlighted_hashes"))
        clear_highlighted_hashes_button = tkinter.Button(buttons_frame,
                           image=self._clear_highlighted_hashes_icon,
                           command=self._handle_clear_highlighted_hashes)
        clear_highlighted_hashes_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(clear_highlighted_hashes_button,
                                             "Clear all highlighted hashes")

        # clear highlighted hashes label
        tkinter.Label(buttons_frame, text="Hashes"
                                        ).pack(side=tkinter.LEFT, anchor="w")

        # register to receive highlight change events
        highlights.set_callback(self._handle_highlight_change)

    def _set_max_hashes_entry(self, max_hashes):
        self.max_hashes_entry.delete(0, tkinter.END)
        if max_hashes == 0:
            self.max_hashes_entry.insert(0, "None")
        else:
            self.max_hashes_entry.insert(0, "%s"%max_hashes)


    def _handle_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            max_hashes = int(self.max_hashes_entry.get())
        except ValueError:
            max_hashes = 0

        # set entry to make sure it looks nice
        self._set_max_hashes_entry(max_hashes)

        # fire if change is from the user
        if not self._is_handle_highlight_change:

            # only set if max_hashes changes
            if max_hashes != self._highlights.max_hashes:
                self._highlights.max_hashes = max_hashes
                self._highlights.fire_change()

    def _handle_highlight_flagged_blocks_selection(self, *args):
        self._highlights.highlight_flagged_blocks = \
                              self._highlight_flagged_blocks_trace_var.get()

        # fire if change is from the user
        if not self._is_handle_highlight_change:
            self._highlights.fire_change()

    def _handle_clear_highlighted_sources(self, *args):
        # clear highlighted sources and signal change
        self._highlights.highlighted_sources.clear()
        self._highlights.fire_change()

    def _handle_clear_highlighted_hashes(self, *args):
        # clear highlighted hashes and signal change
        self._highlights.highlighted_hashes.clear()
        self._highlights.fire_change()

    def _handle_highlight_change(self, *args):
        self._is_handle_highlight_change = True
        self._set_max_hashes_entry(self._highlights.max_hashes)
        self._highlight_flagged_blocks_trace_var.set(
                                   self._highlights.highlight_flagged_blocks)
        self._is_handle_highlight_change = False

