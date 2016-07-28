import colors
import info
from icon_path import icon_path
from tooltip import Tooltip
from scan_image_window import ScanImageWindow
from ingest_window import IngestWindow
from open_window import OpenWindow
from info_window import InfoWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class MenuView():
    """Provides a frame containing munu-level control buttons.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, open_manager, scan_statistics_window, preferences):
        """Args:
          master(a UI container): Parent.
          open_mangaer(OpenManager): Able to open a new dataset.
        """

        # open manager
        self._open_manager = open_manager
        self._scan_statistics_window = scan_statistics_window
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

        # scan statistics button
        self._scan_statistics_icon = tkinter.PhotoImage(file=icon_path("view_scan_statistics"))
        scan_statistics_button = tkinter.Button(button_frame,
                       image=self._scan_statistics_icon,
                       command=self._handle_scan_statistics_window,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        scan_statistics_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(scan_statistics_button, "Show scan statistics")

        # ingest button
        self._ingest_icon = tkinter.PhotoImage(file=icon_path("ingest"))
        ingest_button = tkinter.Button(button_frame, image=self._ingest_icon,
                       command=self._handle_ingest,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        ingest_button.pack(side=tkinter.LEFT)
        Tooltip(ingest_button, "Ingest files into a\nnew hashdb database")

        # scan button
        self._scan_icon = tkinter.PhotoImage(file=icon_path("scan"))
        scan_button = tkinter.Button(button_frame, image=self._scan_icon,
                       command=self._handle_scan,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        scan_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(scan_button, "Scan a media image")

        # offset format preference button
        self._offset_format_preference_icon = tkinter.PhotoImage(
                                file=icon_path("offset_format_preference"))
        offset_format_preference_button = tkinter.Button(button_frame,
                       image=self._offset_format_preference_icon,
                       command=self._handle_offset_format_preference,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        offset_format_preference_button.pack(side=tkinter.LEFT, padx=(0,8))
        Tooltip(offset_format_preference_button,
                  "Toggle offset format between\nsector, decimal, and hex")

        # info button
        self._info_icon = tkinter.PhotoImage(file=icon_path(
                                                              "info"))
        info_button = tkinter.Button(button_frame,
                       image=self._info_icon,
                       command=self._handle_info,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        info_button.pack(side=tkinter.LEFT)
        Tooltip(info_button, "About SectorScope %s" % info.VERSION)


    def _handle_open(self):
        OpenWindow(self.frame, self._open_manager)

    def _handle_scan_statistics_window(self):
        self._scan_statistics_window.show()

    def _handle_ingest(self):
        IngestWindow(self.frame)
        # IngestWindow(self.frame, source_dir='/home/bdallen/KittyMaterial', hashdb_dir='/home/bdallen/Kitty/zzki.hdb')

    def _handle_scan(self):
        ScanImageWindow(self.frame)
        # ScanImageWindow(self.frame, image='/home/bdallen/Kitty/jo-favorites-usb-2009-12-11.E01', hashdb_dir='/home/bdallen/Kitty/KittyMaterial.hdb', output_file='/home/bdallen/Kitty/zz_jo.json')

    def _handle_offset_format_preference(self):
        self._preferences.set_next_offset_format()

    def _handle_info(self):
        InfoWindow(self.frame)

