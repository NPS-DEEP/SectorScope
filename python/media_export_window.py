# Use this to export bytes from a media image to a file.

import os
import sys
import command_runner
from tooltip import Tooltip
from error_window import ErrorWindow
import helpers

try:
    import queue
except ImportError:
    import Queue as queue

try:
    import tkinter
    import tkinter.filedialog as fd
except ImportError:
    import Tkinter as tkinter
    import tkFileDialog as fd

class MediaExportWindow():
    """Export sectors from media to an export file.
    """

    def __init__(self, master, data_manager):
        """Args:
          data_manager(DataManager): Manages scan data and filters.
            Contains the path to the media image.
        """
        # from input parameters
        self._master = master
        self._media_filename = data_manager.media_filename

        # toplevel
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("Export Media Bytes to File")

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
                                            text="Ingest",
                                            padx=8, pady=8)

        # export_filename label
        tkinter.Label(required_frame, text="Output File") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # export_filename input entry
        self._export_filename_entry = tkinter.Entry(required_frame, width=40)
        self._export_filename_entry.grid(row=0, column=1, sticky=tkinter.W,
                                          padx=8)

        # export_filename chooser button
        export_filename_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_export_filename_chooser)
        export_filename_entry_button.grid(row=0, column=2, sticky=tkinter.W)

        # offset label for offset into media
        tkinter.Label(required_frame, text="Sector Offset") \
                          .grid(row=1, column=0, sticky=tkinter.W)

        # offset entry for offset into media
        self._offset_entry = tkinter.Entry(required_frame, width=16)
        self._offset_entry.grid(row=1, column=1, sticky=tkinter.W, padx=8)

        # count label for number of sectors to export
        tkinter.Label(required_frame, text="Sectors to Export") \
                          .grid(row=2, column=0, sticky=tkinter.W)

        # count entry for number of sectors to export
        self._count_entry = tkinter.Entry(required_frame, width=16)
        self._count_entry.grid(row=2, column=1, sticky=tkinter.W, padx=8)

        # make new export file checkbutton
        self._is_new_int_var = tkinter.IntVar()
        self._is_new_int_var.set(True)
        self._is_new_checkbutton = tkinter.Checkbutton(required_frame,
                    text="Make New Export File",
                    variable = self._is_new_int_var,
                    bd=0, pady=4, highlightthickness=0)
        self._is_new_checkbutton.grid(row=3, column=0)

        return required_frame

    def _make_button_frame(self, master):
        button_frame = tkinter.Frame(master)

        # export button
        self._export_button = tkinter.Button(button_frame, text="Export",
                                            command=self._handle_export)
        self._export_button.pack(side=tkinter.LEFT, padx=8)

        # close button
        self._close_button = tkinter.Button(button_frame, text="Close",
                                             command=self._handle_close)
        self._close_button.pack(side=tkinter.LEFT, padx=8)

        return button_frame

    def _handle_export_filename_chooser(self, *args):
        export_filename = fd.asksaveasfilename(
                               title="Open Export file")
        if export_filename:
            self._export_filename_entry.delete(0, tkinter.END)
            self._export_filename_entry.insert(0, export_filename)

    def _handle_export(self):
        # get export file filename
        export_filename = os.path.abspath(self._export_filename_entry.get())
        self._export_filename_entry.delete(0, tkinter.END)
        self._export_filename_entry.insert(0, export_filename)

        # get byte offset
        try:
            byte_offset = int(self._offset_entry.get()) * 512
        except ValueError:
            ErrorWindow(self._master, "Export Error",
                        "Invalid sector offset value: '%s'." %
                                  self._offset_entry.get())
            return

        # get byte count
        try:
            byte_count = int(self._count_entry.get()) * 512
        except ValueError:
            ErrorWindow(self._master, "Export Error",
                        "Invalid sector count value: '%s'." %
                                  self._count_entry.get())
            return

        # new file else append to file
        if self._is_new_int_var.get():
            # new file must not exist yet
            if os.path.exists(export_filename):
                ErrorWindow(self._master, "Export Error",
                            "File '%s' already exists." % export_filename)
                return

            # open mode for new file
            open_mode = 'wb' # write binary
        else:
            # open mode for existing file
            open_mode = 'ab' # append binary

        # read the media bytes
        error_message, media_bytes = helpers.read_media_bytes(
                       self._media_filename, byte_offset, byte_count)
        if error_message:
            ErrorWindow(self._master, "Export Error", error_message)
            return

        # write to file
        try:
            f = open(export_filename, open_mode)
            f.write(media_bytes)
            f.close()
        except Exception as e:
            ErrorWindow(self._master, "Export Error", e)
            return

        # here so export worked so close window
        self._root_window.destroy()

    def _handle_close(self):
        self._root_window.destroy()

