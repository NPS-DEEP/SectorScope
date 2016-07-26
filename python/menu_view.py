import colors
from icon_path import icon_path
from tooltip import Tooltip
from scan_image_window import ScanImageWindow
from ingest_window import IngestWindow
from open_window import OpenWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class MenuView():
    """Provides a frame containing munu-level control buttons.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, open_manager, project_window, preferences):
        """Args:
          master(a UI container): Parent.
          open_mangaer(OpenManager): Able to open a new dataset.
        """

        # open manager
        self._open_manager = open_manager
        self._project_window = project_window
        self._preferences = preferences

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # make the frame for the control buttons
        button_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        button_frame.pack(side=tkinter.TOP, anchor="w")

        # open button
        self._open_icon = tkinter.PhotoImage(file=icon_path("open"))
        open_button = tkinter.Button(button_frame,
                       image=self._open_icon, command=self._handle_open,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        open_button.pack(side=tkinter.LEFT)
        Tooltip(open_button, "Open scanned output")

        # project properties button
        self._project_icon = tkinter.PhotoImage(file=icon_path("view_project"))
        project_button = tkinter.Button(button_frame,
                       image=self._project_icon,
                       command=self._handle_project_window,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        project_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(project_button, "Show project statistics")

        # import button
        self._import_icon = tkinter.PhotoImage(file=icon_path("import"))
        import_button = tkinter.Button(button_frame, image=self._import_icon,
                       command=self._handle_import,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        import_button.pack(side=tkinter.LEFT)
        Tooltip(import_button, "Import from files into a\nnew hashdb database")

        # scan button
        self._scan_icon = tkinter.PhotoImage(file=icon_path("scan"))
        scan_button = tkinter.Button(button_frame, image=self._scan_icon,
                       command=self._handle_scan,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        scan_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(scan_button, "Scan a media image")

        # preferences button
        self._preferences_icon = tkinter.PhotoImage(file=icon_path(
                                                              "preferences"))
        preferences_button = tkinter.Button(button_frame,
                       image=self._preferences_icon,
                       command=self._handle_preferences,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        preferences_button.pack(side=tkinter.LEFT)
        Tooltip(preferences_button, "Toggle format preference between hex,\n"
                                    "decimal, and sector (usually sector)")

    def _handle_open(self):
        OpenWindow(self.frame, self._open_manager)

    def _handle_project_window(self):
        self._project_window.show()

    def _handle_scan(self):
        ScanImageWindow(self.frame)
    #        ScanImageWindow(self.frame, image='/home/bdallen/Kitty/jo-favorites-usb-2009-12-11.E01', hashdb_dir='/home/bdallen/zzz5', output_file='/home/bdallen/zzzout5.json')

    def _handle_preferences(self):
        self._preferences.set_next()

    def _handle_import(self):
        IngestWindow(self.frame)

