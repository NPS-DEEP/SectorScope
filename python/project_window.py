from forensic_path import size_string, offset_string
import colors
import helpers
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ProjectWindow():
    """Provides a window to show opened project attributes.
    """
    def __init__(self, master, data_manager, preferences):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages project data and filters.
         """
        # variables
        self._data_manager = data_manager
        self._preferences = preferences

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Project Statistics")
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
        self._scan_file_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._scan_file_text.pack(side=tkinter.TOP, anchor="w")

        # media image
        self._image_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._image_text.pack(side=tkinter.TOP, anchor="w")

        # media image size
        self._image_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._image_size_text.pack(side=tkinter.TOP, anchor="w")

        # hashdb database path
        self._database_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._database_text.pack(side=tkinter.TOP, anchor="w")

        # block size
        self._block_size_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._block_size_text .pack(side=tkinter.TOP, anchor="w")

        # size statistics
        self._sizes_text = tkinter.Label(f, bg=colors.BACKGROUND)
        self._sizes_text.pack(side=tkinter.TOP, anchor="w")

        # register to receive data manager change events
        data_manager.set_callback(self._handle_data_manager_change)

        # register to receive preferences change events
        preferences.set_callback(self._handle_data_manager_change)

        # set initial state
        self._handle_data_manager_change()

        # start with window hidden
        self._root_window.withdraw()

    # this function is registered to and called by IdentifiedData
    def _handle_data_manager_change(self, *args):
        if self._data_manager.image_filename:
            # data_manager opened
            self._scan_file_text["text"] = 'Match file: %s' % \
                               self._data_manager.scan_file
            self._image_text["text"] = 'Image: %s' % \
                               self._data_manager.image_filename
            self._image_size_text["text"] = 'Image size: %s  (%s)' % (
                               size_string(self._data_manager.image_size),
                               offset_string(self._data_manager.image_size,
                                      self._preferences.offset_format))
            self._database_text["text"] = 'Database: %s' % \
                               self._data_manager.hashdb_dir
            self._block_size_text["text"] = 'Block size: %s' % (
                                      self._data_manager.image_block_size)
            self._sizes_text["text"] = 'Scan matches: Paths: %s        ' \
                                  'Hashes: %s        Sources: %s' % (
                             self._data_manager.len_forensic_paths,
                             self._data_manager.len_hashes,
                             self._data_manager.len_sources)

        else:
            # data_manager not opened
            self._scan_file_text["text"] = 'Scan file: Not opened'
            self._image_text["text"] = 'Image: Not opened'
            self._image_size_text["text"] = 'Image size: Not opened'
            self._database_text["text"] = 'Database: Not opened'
            self._block_size_text["text"] = 'Block size: Not opened'
            self._sizes_text["text"] = 'Scan matches: Not opened'

    def show(self):
        self._root_window.deiconify()
        self._root_window.lift()

    def _hide(self):
        self._root_window.withdraw()

