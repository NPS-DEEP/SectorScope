# Use this to scan for hashes.
# Relative paths are replaced with absolute paths.

import os
import sys
import helpers
from tooltip import Tooltip
try:
    import tkinter
    import tkinter.filedialog as fd
except ImportError:
    import Tkinter as tkinter
    import tkFileDialog as fd

class OpenWindow():
    """Open a scan file to view matches.
    """

    def __init__(self, master, open_manager,
                 scan_file="", sector_size=512,
                 alternate_media_filename="", alternate_hashdb_dir=""):

        """Args:
          scan_file(str): The block hash scan file containing the matching
                          identified blocks.
          sector_size(int): The minimum resolution to zoom down to.
          alternate_media_filename(str): The media image that the scan came from
                                         or leave blank for default.
          alternate_media_filename(str): The hashdb_dir used by the scan
                                         or leave blank for default.
        """
        # input parameters
        self._open_manager = open_manager
        self._scan_file = scan_file
        self._sector_size = sector_size
        self._alternate_media_filename = alternate_media_filename
        self._alternate_hashdb_dir = alternate_hashdb_dir

        # toplevel
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Open Scan File")

        # make the control frame
        control_frame = tkinter.Frame(self._root_window, borderwidth=1,
                                      relief=tkinter.RIDGE)
        control_frame.pack(side=tkinter.TOP)

        # add required parameters frame to the control frame
        required_frame = self._make_required_frame(control_frame)
        required_frame.pack(side=tkinter.TOP, anchor="w", padx=8, pady=8)

        # add button frame to the root window
        button_frame = self._make_button_frame(self._root_window)
        button_frame.pack(side=tkinter.TOP, padx=8, pady=8)

    def _make_required_frame(self, master):
        required_frame = tkinter.LabelFrame(master,
                                            text="Open Scan File",
                                            padx=8, pady=8)

        # scan_file label
        tkinter.Label(required_frame, text="Scan File") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # scan_file input entry
        self._scan_file_entry = tkinter.Entry(required_frame, width=40)
        self._scan_file_entry.grid(row=0, column=1, sticky=tkinter.W,
                                          padx=8)
        self._scan_file_entry.insert(0, self._scan_file)

        # scan_file chooser button
        scan_file_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_scan_file_chooser)
        scan_file_entry_button.grid(row=0, column=2, sticky=tkinter.W)

        # media image label
        tkinter.Label(required_frame, text="Alternate Media Image") \
                          .grid(row=1, column=0, sticky=tkinter.W)

        # alternate media image entry
        self._media_filename_entry = tkinter.Entry(required_frame, width=40)
        self._media_filename_entry.grid(row=1, column=1, sticky=tkinter.W,
                                          padx=8)
        self._media_filename_entry.insert(0, self._alternate_media_filename)
        Tooltip(self._media_filename_entry, "Alternate media image, leave blank"
                                         "\nto use the default from scan file")

        # alternate media image chooser button
        media_filename_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_media_filename_chooser)
        media_filename_entry_button.grid(row=1, column=2, sticky=tkinter.W)

        # alternate hashdb_dir label
        tkinter.Label(required_frame, text="Alternate Hash Database") \
                          .grid(row=2, column=0, sticky=tkinter.W)

        # alternate hashdb_dir
        self._hashdb_dir_entry = tkinter.Entry(required_frame, width=40)
        self._hashdb_dir_entry.grid(row=2, column=1, sticky=tkinter.W,
                                          padx=8)
        self._hashdb_dir_entry.insert(0, self._alternate_hashdb_dir)
        Tooltip(self._hashdb_dir_entry, "Alternate hash database, leave blank"
                                         "\nto use the default from scan file")

        # alternate media image chooser button
        hashdb_dir_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_hashdb_dir_chooser)
        hashdb_dir_entry_button.grid(row=2, column=2, sticky=tkinter.W)

        # sector size label
        tkinter.Label(required_frame, text="Sector Size") \
                          .grid(row=3, column=0, sticky=tkinter.W)

        # sector size entry
        self._sector_size_entry = tkinter.Entry(required_frame, width=8)
        self._sector_size_entry.grid(row=3, column=1, sticky=tkinter.W, padx=8)
        self._sector_size_entry.insert(0, self._sector_size)

        return required_frame

    def _make_button_frame(self, master):
        button_frame = tkinter.Frame(master)

        # open button
        self._open_button = tkinter.Button(button_frame, text="Open",
                                            command=self._handle_open)
        self._open_button.pack(side=tkinter.LEFT, padx=8)

        # cancel button
        self._cancel_button = tkinter.Button(button_frame, text="Cancel",
                                             command=self._handle_cancel)
        self._cancel_button.pack(side=tkinter.LEFT, padx=8)

        return button_frame

    def _handle_media_filename_chooser(self, *args):
        media_file = fd.askopenfilename(title="Open Alternate Media Image")
        if media_file:
            self._media_filename_entry.delete(0, tkinter.END)
            self._media_filename_entry.insert(0, media_file)

    def _handle_hashdb_dir_chooser(self, *args):
        media_file = fd.askdirectory(title="Open Alternate Hash Database",
                                     mustexist=True)
        if media_file:
            self._hashdb_dir_entry.delete(0, tkinter.END)
            self._hashdb_dir_entry.insert(0, media_file)

    def _handle_scan_file_chooser(self, *args):
        file_opt={"title":"Open Scan Match File", "defaultextension":".json"}
        scan_file = fd.askopenfilename(**file_opt)
        if scan_file:
            self._scan_file_entry.delete(0, tkinter.END)
            self._scan_file_entry.insert(0, scan_file)

    def _handle_open(self):
        # get scan_file field
        scan_file = os.path.abspath(self._scan_file_entry.get())
        if not os.path.exists(scan_file):
            ErrorWindow(self._master, "Open Error",
                              "Unable to open scan file %s" % scan_file)
            return

        # get sector size
        try:
            sector_size = int(self._sector_size_entry.get())
        except ValueError:
            ErrorWindow(self._master, "Open Error",
                                "Invalid sector size: '%s'" %
                                self._sector_size_entry.get())
            return

        # get alternate media image field
        alternate_media_filename = self._media_filename_entry.get()
        if alternate_media_filename:
            alternate_media_filename = os.path.abspath(alternate_media_filename)
            if not os.path.exists(alternate_image_filename):
                ErrorWindow(self._master, "Open Error",
                    "Unable to find alternate media image file %s" % scan_file)
                return

        # get alternate hashdb_dir field
        alternate_hashdb_dir = self._hashdb_dir_entry.get()
        if alternate_hashdb_dir:
            alternate_hashdb_dir = os.path.abspath(alternate_hashdb_dir)
            if not os.path.exists(alternate_hashdb_dir):
                ErrorWindow(self._master, "Open Error",
                    "Unable to find alternate media image file %s" % scan_file)
                return

        self._open_manager.open_scan_file(scan_file, sector_size,
                              alternate_media_filename, alternate_hashdb_dir);

    def _handle_cancel(self):
        self._root_window.destroy()

