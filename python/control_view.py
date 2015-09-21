import tkinter 
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow

class ControlView():
    """Provides a frame containing user controls including launchers
    and highlight control.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, highlights, open_manager):
        """Args:
          master(a UI container): Parent.
          highlights(Highlights): Highlights for hashes and sources.
          open_mangaer(OpenManager): Able to open a new dataset.
        """

        # highlights
        self._highlights = highlights

        # open manager
        self._open_manager = open_manager

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # make the frame for the control buttons
        button_frame = tkinter.Frame(self.frame)
        button_frame.pack(side=tkinter.TOP, anchor="w")

        # open button
        self._open_icon = tkinter.PhotoImage(file=icon_path("open"))
        open_button = tkinter.Button(button_frame,
                       image=self._open_icon, command=self._handle_open)
        open_button.pack(side=tkinter.LEFT)
        Tooltip(open_button, "Open scanned output")

        # scan button
        self._scan_icon = tkinter.PhotoImage(file=icon_path("scan"))
        scan_button = tkinter.Button(button_frame, image=self._scan_icon,
                       command=self._handle_scan)
        scan_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(scan_button, "Scan a media iamge")

        # import button
        self._import_icon = tkinter.PhotoImage(file=icon_path("import"))
        import_button = tkinter.Button(button_frame, image=self._import_icon,
                       command=self._handle_import)
        import_button.pack(side=tkinter.LEFT)
        Tooltip(import_button, "Import files into a\nnew hashdb database")

        # max hashes entry
        max_hashes_frame = tkinter.Frame(self.frame)
        max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(max_hashes_frame, text="Max Same Hashes:") \
                                        .pack(side=tkinter.LEFT, anchor="w")
        self.max_hashes_entry = tkinter.Entry(max_hashes_frame, width=6)
        self.max_hashes_entry.insert(0, "None")
        self.max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")
        self.max_hashes_entry.bind('<Return>',
                                   self._handle_max_hashes_selection, add='+')
        self.max_hashes_entry.bind('<FocusOut>',
                                   self._handle_max_hashes_selection, add='+')

        # set up the local checkbutton trace var so change function gets called
        self._highlight_flagged_blocks_trace_var = tkinter.IntVar()
        self._highlight_flagged_blocks_trace_var.set(
                                         highlights.highlight_flagged_blocks)
        self._highlight_flagged_blocks_trace_var.trace_variable('w',
                             self._handle_highlight_flagged_blocks_selection)

        # highlight_flagged_blocks checkbutton
        self.highlight_flagged_blocks_checkbutton = tkinter.Checkbutton(
                           self.frame, text="Highlight Flagged Blocks",
                           variable=self._highlight_flagged_blocks_trace_var,
                           bd=0,padx=0,pady=0)
        self.highlight_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                    anchor="w")

    def _handle_open(self):
        self._open_manager.open_be_dir("")

    def _handle_scan(self):
        BEScanWindow(self.frame)

    def _handle_import(self):
        BEImportWindow(self.frame)

    def _handle_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            max_hashes = int(self.max_hashes_entry.get())
        except ValueError:
            max_hashes = 0

        # set entry to make sure it looks nice
        self.max_hashes_entry.delete(0, tkinter.END)
        if max_hashes == 0:
            self.max_hashes_entry.insert(0, "None")
        else:
            self.max_hashes_entry.insert(0, "%s"%max_hashes)

        # only set if max_hashes changes
        if max_hashes != self._highlights.max_hashes:
            self._highlights.max_hashes = max_hashes
            self._highlights.fire_change()

    def _handle_highlight_flagged_blocks_selection(self, *args):
        self._highlights.highlight_flagged_blocks = \
                              self._highlight_flagged_blocks_trace_var.get()
        self._highlights.fire_change()

