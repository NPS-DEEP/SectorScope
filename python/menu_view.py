import colors
from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class MenuView():
    """Provides a frame containing munu-level control buttons.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, open_manager, project_window):
        """Args:
          master(a UI container): Parent.
          open_mangaer(OpenManager): Able to open a new dataset.
        """

        # open manager
        self._open_manager = open_manager
        self._project_window = project_window

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
        project_button.pack(side=tkinter.LEFT)
        Tooltip(project_button, "Show opened project properties")

        # import button
        self._import_icon = tkinter.PhotoImage(file=icon_path("import"))
        import_button = tkinter.Button(button_frame, image=self._import_icon,
                       command=self._handle_import,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        import_button.pack(side=tkinter.LEFT, padx=(8,4))
        Tooltip(import_button, "Import files into a\nnew hashdb database")

        # scan button
        self._scan_icon = tkinter.PhotoImage(file=icon_path("scan"))
        scan_button = tkinter.Button(button_frame, image=self._scan_icon,
                       command=self._handle_scan,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        scan_button.pack(side=tkinter.LEFT)
        Tooltip(scan_button, "Scan a media image")

    def _handle_open(self):
        self._open_manager.open_be_dir("")

    def _handle_project_window(self):
        self._project_window.show()

    def _handle_scan(self):
        BEScanWindow(self.frame)

    def _handle_import(self):
        BEImportWindow(self.frame)

