import tkinter 
import identified_data
import filters

class OpenManager():
    """Opens a bulk_extractor directory, sets data, and fires events.
 
    Attributes:
      frame(Frame): The containing frame for this view.
      active_be_dir(str): The be_dir currently open, or "".
    """

    def __init__(self, master, identified_data, filters,
                 byte_offset_selection_trace_var):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          byte_offset_selection_trace_var(tkinter Var): Variable to
            communicate selection change.
        """

        # local references
        self._master = master
        self._identified_data = identified_data
        self._filters = filters
        self._byte_offset_selection_trace_var = byte_offset_selection_trace_var

        # state
        active_be_dir = identified_data.be_dir

    def open_be_dir(self, be_dir):
        # read be_dir else show error window
        try:
            self._identified_data.read(be_dir)

        except Exception as e:
            self._show_error(e)
            return

        # set the views for the opened data
        # clear any byte offset selection
        self._byte_offset_selection_trace_var.set(-1)

        # clear any filter settings
        self._filters.clear()

    def open_chooser_dir(self):
        """Open be_dir selected in modal chooser else report error."""
        # get be_dir from chooser
        be_dir = tkinter.filedialog.askdirectory(
                     title="Open bulk_extractor directory",
                     mustexist=True, initialdir=self._identified_data.be_dir)

        # open be_dir
        self.open_be_dir(be_dir)

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




