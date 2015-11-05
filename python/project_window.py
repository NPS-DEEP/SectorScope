from forensic_path import size_string, offset_string
import colors
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ProjectWindow():
    """Provides a window to show opened project attributes.
    """
    def __init__(self, master, identified_data, preferences):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
        """
        # variables
        self._identified_data = identified_data
        self._preferences = preferences

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Project Attributes")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._hide)

        # make the containing frame
        f = tkinter.Frame(self._root_window, padx=8, pady=8,
                                                       bg=colors.BACKGROUND)
        f.pack()

        # title
        tkinter.Label(f, text="Project", bg=colors.BACKGROUND).pack(
                                             side=tkinter.TOP, pady=(0,4))

        # scan path
        self._scan_path_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._scan_path_text.pack(side=tkinter.TOP, anchor="w")

        # media image
        self._image_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._image_text.pack(side=tkinter.TOP, anchor="w")

        # media image size
        self._image_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._image_size_text.pack(side=tkinter.TOP, anchor="w")

        # hashdb database path
        self._database_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._database_text.pack(side=tkinter.TOP, anchor="w")

        # size statistics
        self._sizes_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._sizes_text.pack(side=tkinter.TOP, anchor="w")

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # register to receive preferences change events
        preferences.set_callback(self._handle_identified_data_change)

        # set initial state
        self._handle_identified_data_change()

        # start with window hidden
        self._root_window.withdraw()

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):
        if self._identified_data.image_filename:
            # identified_data opened
            self._scan_path_text["text"] = 'Scan path: %s' % \
                               self._identified_data.be_dir
            self._image_text["text"] = 'Image: %s' % \
                               self._identified_data.image_filename
            self._image_size_text["text"] = 'Image size: %s  (%s)' % (
                               size_string(self._identified_data.image_size),
                               offset_string(self._identified_data.image_size,
                                      self._preferences.offset_format,
                                      self._identified_data.sector_size))
            self._database_text["text"] = 'Database: %s' % \
                               self._identified_data.hashdb_dir
            self._sizes_text["text"] = 'Matches: Paths: %s        ' \
                                  'Hashes: %s        Sources: %s' % (
                             len(self._identified_data.forensic_paths),
                             len(self._identified_data.hashes),
                             len(self._identified_data.source_details))

        else:
            # identified_data not opened
            self._scan_path_text["text"] = 'Scan path: Not opened'
            self._image_text["text"] = 'Image: Not opened'
            self._image_size_text["text"] = 'Image size: Not opened'
            self._database_text["text"] = 'Database: Not opened'
            self._database_text["text"] = 'Matches: Not opened'

    def show(self):
        self._root_window.deiconify()
        self._root_window.lift()

    def _hide(self):
        self._root_window.withdraw()

