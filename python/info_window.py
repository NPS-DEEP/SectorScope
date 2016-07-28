from forensic_path import size_string, offset_string
import colors
import helpers
import info
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class InfoWindow():
    """Provides a window to show SectorScope version and web page
    """
    def __init__(self, master):
        """Args:
          master(a UI container): Parent.
         """

        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("About SectorScope")
        self._root_window.transient(master)
        self._root_window.protocol('WM_DELETE_WINDOW', self._hide)

        # make the containing frame
        f = tkinter.Frame(self._root_window, padx=18, pady=18,
                                                       bg=colors.BACKGROUND)
        f.pack()

        # sectorScope version
        tkinter.Label(f, text="SectorScope Version: %s" % info.VERSION,
                  bg=colors.BACKGROUND).pack(side=tkinter.TOP, anchor="w")

        # hashdb version
        tkinter.Label(f, text="hashdb Version: %s" %
                  helpers.read_hashdb_version().strip(),
                  bg=colors.BACKGROUND).pack(side=tkinter.TOP, anchor="w")

    def show(self):
        self._root_window.deiconify()
        self._root_window.lift()

    def _hide(self):
        self._root_window.withdraw()

