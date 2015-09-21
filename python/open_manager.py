import tkinter 
import identified_data
import highlights

class OpenManager():
    """Opens a bulk_extractor directory, sets data, and fires events.
 
    Attributes:
      frame(Frame): The containing frame for this view.
      active_be_dir(str): The be_dir currently open, or "".
    """

    def __init__(self, master, identified_data, highlights, offset_selection,
                                                         range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          highlights(Highlights): Highlights that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
        """

        # local references
        self._master = master
        self._identified_data = identified_data
        self._highlights = highlights
        self._offset_selection = offset_selection
        self._range_selection = range_selection

        # state
        active_be_dir = identified_data.be_dir

    """Open be_dir or if not be_dir open be_dir from chooser."""
    def open_be_dir(self, be_dir):
        if not be_dir:
            # get be_dir from chooser
            be_dir = tkinter.filedialog.askdirectory(
                     title="Open bulk_extractor directory",
                     mustexist=True, initialdir=self._identified_data.be_dir)

        if not be_dir:
            # user did not choose, so abort
            return

        # read be_dir else show error window
        try:
            self._identified_data.read(be_dir)

        except Exception as e:
            self._show_error(e)
            return

        # clear any byte offset selection
        self._offset_selection.clear()

        # clear any highlight settings
        self._highlights.clear()

        # clear any byte range selection
        self._range_selection.clear()

    def _show_error(self, e):
        # make toplevel window
        self._root_window = tkinter.Toplevel(self._master)
        self._root_window.title("Open Error")
        self._root_window.transient(self._master)

        tkinter.Label(self._root_window, text="Error:").pack( \
                            side=tkinter.TOP, padx=8, pady=(8,0), anchor="w")
        error_text = tkinter.Text(self._root_window, width=60, height=8, bd=0)
        error_text.pack(anchor="w", padx=8, pady=0)
        error_text.insert(tkinter.END, "%s\n" %e)
        error_text.config(state=tkinter.DISABLED)
        tkinter.Button(self._root_window, text="OK",
                       command=self._handle_ok).pack( \
                            side=tkinter.TOP, padx=8, pady=8)

    def _handle_ok(self):
        self._root_window.destroy()




