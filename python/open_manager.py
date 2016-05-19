from error_window import ErrorWindow
from data_reader import DataReader
try:
    import tkinter
    import tkinter.filedialog as fd
except ImportError:
    import Tkinter as tkinter
    import tkFileDialog as fd

class OpenManager():
    """Opens a bulk_extractor directory, sets data, and fires events.

    Attributes:
      frame(Frame): The containing frame for this view.
    """

    def __init__(self, master, data_manager, annotation_filter,
                 histogram_control, preferences):
        """Args:
          master(a UI container): Parent.
          data_reader(DataReader): Data reader.
          data_manager(DataManager): Manages project data and filters.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
           preferences(Preferences): Preference, namely the offset format.
        """

        # local references
        self._master = master
        self._data_manager = data_manager
        self._annotation_filter = annotation_filter
        self._histogram_control = histogram_control
        self._preferences = preferences

        self._data_reader = DataReader()

    """Open match_file or if "" then open match_file from chooser."""
    def open_match_file(self, match_file):
        if not match_file:
            # get match_file from chooser
            match_file = fd.askopenfilename(
                     title="Open Scan Match File",
                     defaultextension=".json",
                     initialdir=self._data_manager.match_file)

        if not match_file:
            # user did not choose, so abort
            return

        # read match_file else show error window
        try:
            self._data_reader.read(match_file)

        except Exception as e:
            ErrorWindow(self._master, "Open Error", e)
            return

        # the read worked so accept the the project

        # report if annotation reader failed
        if self._data_reader.annotation_load_status:
            ErrorWindow(self._master, "Annotation Read Error",
                              "Unable to read media image annotations.\n"
                              "Please check that TSK is installed "
                              "and that PATH is set.\n%s" %
                              self._data_reader.annotation_load_status)

        # clear annotation filter settings
        self._annotation_filter.set([])

        # reset the histogram control settings
        self._histogram_control.set_project(self._data_reader.image_size,
                                            self._data_reader.block_size)

        # accept the data, firing change
        self._data_manager.set_data(self._data_reader)

