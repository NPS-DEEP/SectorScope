#!/usr/bin/env python3
# Use this to import hashes from a directory into a hash database.
# Relative paths will be replaced with absolute paths.

import queue
import os
import sys
import tkinter
import tkinter.filedialog
import threaded_subprocess

class BEImportGUI():
    """Performs import using a GUI interface.
    """

    def __init__(self, args):
        """Args:
          args(dict): The invocation argument list.
        """
        # the queue for import text
        self._queue = queue.Queue()

        # root
        root_window = tkinter.Tk()
        root_window.title("Block Match Import")

        # local reference to args
        self._args = args

        # make the control frame
        control_frame = tkinter.Frame(root_window, borderwidth=1, relief=tkinter.RIDGE)
        control_frame.pack(side=tkinter.TOP)

        # add required parameters frame to the control frame
        required_frame = self._make_required_frame(control_frame)
        required_frame.pack(side=tkinter.TOP, anchor="w", padx=8, pady=8)

        # add optional parameters frame to the control frame
        optional_frame = self._make_optional_frame(control_frame)
        optional_frame.pack(side=tkinter.TOP, anchor="w", padx=8, pady=0)

        # add progress frame to the control frame
        progress_frame = self._make_progress_frame(control_frame)
        progress_frame.pack(side=tkinter.TOP, anchor="w", padx=8, pady=8)

        # add button frame to the root window
        button_frame = self._make_button_frame(root_window)
        button_frame.pack(side=tkinter.TOP, padx=8, pady=8)

        # main loop
        root_window.mainloop()

    def _make_required_frame(self, master):
        required_frame = tkinter.LabelFrame(master,
                                            text="Required Parameters",
                                            padx=8, pady=8)

        # source directory label
        tkinter.Label(required_frame, text="Input Source Directory") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # source directory entry
        self._source_directory_entry = tkinter.Entry(required_frame, width=40)
        self._source_directory_entry.grid(row=0, column=1, sticky=tkinter.W,
                                          padx=8)
        self._source_directory_entry.insert(0, self._args.source_dir)

        # source directory chooser button
        source_directory_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_source_directory_chooser)
        source_directory_entry_button.grid(row=0, column=2, sticky=tkinter.W)

        # bulk_extractor output directory label
        tkinter.Label(required_frame, text="bulk_extractor Output Directory") \
                          .grid(row=1, column=0, sticky=tkinter.W)

        # bulk_extractor output directory input entry
        self._output_directory_entry = tkinter.Entry(required_frame, width=40)
        self._output_directory_entry.grid(row=1, column=1, sticky=tkinter.W,
                                          padx=8)
        self._output_directory_entry.insert(0, self._args.be_dir)

        # bulk_extractor output directory chooser button
        output_directory_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_output_directory_chooser)
        output_directory_entry_button.grid(row=1, column=2, sticky=tkinter.W)

        return required_frame

    def _make_optional_frame(self, master):
        optional_frame = tkinter.LabelFrame(master,
                                            text="Options",
                                            padx=8, pady=8)

        # block size label
        tkinter.Label(optional_frame, text="Block Size") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # block size entry
        self._block_size_entry = tkinter.Entry(optional_frame, width=8)
        self._block_size_entry.grid(row=0, column=1, sticky=tkinter.W, padx=8)
        self._block_size_entry.insert(0, self._args.block_size)

        # sector size label
        tkinter.Label(optional_frame, text="Sector Size") \
                          .grid(row=1, column=0, sticky=tkinter.W)

        # sector size entry
        self._sector_size_entry = tkinter.Entry(optional_frame, width=8)
        self._sector_size_entry.grid(row=1, column=1, sticky=tkinter.W, padx=8)
        self._sector_size_entry.insert(0, self._args.sector_size)

        # repository name label
        tkinter.Label(optional_frame, text="Repository Name") \
                          .grid(row=2, column=0, sticky=tkinter.W)

        # repository name entry
        self._repository_name_entry = tkinter.Entry(optional_frame, width=40)
        self._repository_name_entry.grid(row=2, column=1, sticky=tkinter.W,
                                         padx=(8,0))
        self._repository_name_entry.insert(0, self._args.repository_name)

        return optional_frame

    def _make_progress_frame(self, master):
        progress_frame = tkinter.Frame(master)

        # Log label
        tkinter.Label(progress_frame, text="Progress") \
                           .pack(side=tkinter.TOP, anchor="w")

        # scroll frame
        scroll_frame = tkinter.Frame(progress_frame, bd=1,
                                     relief=tkinter.SUNKEN)
        scroll_frame.pack()
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

        # xscrollbar in scroll frame
        xscrollbar = tkinter.Scrollbar(scroll_frame, bd=0,
                                       orient=tkinter.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=tkinter.E + tkinter.W)

        # yscrollbar in scroll frame
        yscrollbar = tkinter.Scrollbar(scroll_frame, bd=0)
        yscrollbar.grid(row=0, column=1, sticky=tkinter.N + tkinter.S)

        # text area in scroll frame
        TEXT_WIDTH=80
        TEXT_HEIGHT=12
        self._progress_text = tkinter.Text(scroll_frame, wrap=tkinter.NONE,
                                     width=TEXT_WIDTH, height=TEXT_HEIGHT,
                                     bd=0,
                                     xscrollcommand=xscrollbar.set,
                                     yscrollcommand=yscrollbar.set)
        self._progress_text.grid(row=0, column=0, sticky=tkinter.N +
                                 tkinter.S + tkinter.E + tkinter.W)

        xscrollbar.config(command=self._progress_text.xview)
        yscrollbar.config(command=self._progress_text.yview)

        # status frame
        status_frame = tkinter.Frame(progress_frame)
        status_frame.pack(side=tkinter.TOP, anchor="w")

        # status "Status:" title
        tkinter.Label(status_frame, text="Status:").pack(side=tkinter.LEFT)

        # status label
        self._status_label = tkinter.Label(status_frame,
                                           text="Not started")
        self._status_label.pack(side=tkinter.LEFT)

        return progress_frame

    def _make_button_frame(self, master):
        button_frame = tkinter.Frame(master)

        # start button
        self._start_button = tkinter.Button(button_frame, text="Start",
                                            command=self._handle_start)
        self._start_button.pack(side=tkinter.LEFT, padx=8)

        # cancel button
        self._cancel_button = tkinter.Button(button_frame, text="Cancel",
                                             command=self._handle_cancel,
                                             state=tkinter.DISABLED)
        self._cancel_button.pack(side=tkinter.LEFT, padx=8)

        # close button
        self._close_button = tkinter.Button(button_frame, text="Close",
                                            command=self._handle_close)
        self._close_button.pack(side=tkinter.LEFT, padx=8)

        return button_frame

    def _set_status_text(self, text):
        self._status_label["text"] = text

        # also put status into progress text
        self._progress_text.insert(tkinter.END, "%s\n" % text)

    def _set_running(self):
        self._set_status_text("Running...")
        self._start_button.config(state=tkinter.DISABLED)
        self._cancel_button.config(state=tkinter.NORMAL)
        self._close_button.config(state=tkinter.DISABLED)

    def _set_done(self):
        self._set_status_text("Done.")
        self._start_button.config(state=tkinter.NORMAL)
        self._cancel_button.config(state=tkinter.DISABLED)
        self._close_button.config(state=tkinter.NORMAL)

    def _set_failed(self):
        self._set_status_text("Failed.")
        self._start_button.config(state=tkinter.NORMAL)
        self._cancel_button.config(state=tkinter.DISABLED)
        self._close_button.config(state=tkinter.NORMAL)

    def _handle_source_directory_chooser(self, *args):
        source_directory = tkinter.filedialog.askdirectory(
                               title="Open Input Source Directory",
                               mustexist=True)
        self._source_directory_entry.delete(0, tkinter.END)
        self._source_directory_entry.insert(0, source_directory)

    def _handle_output_directory_chooser(self, *args):
        output_directory = tkinter.filedialog.askdirectory(
                               title="Open bulk_extractor output Directory",
                               mustexist=False)
        self._output_directory_entry.delete(0, tkinter.END)
        self._output_directory_entry.insert(0, output_directory)

    def _handle_consume_queue(self):
        # consume the queue
        while not self._queue.empty():
            self._progress_text.insert(tkinter.END, self._queue.get())

        # more or done
        if self._threaded_subprocess.is_alive():
            # keep progress_text consuming queue
            self._progress_text.after(200, self._handle_consume_queue)
        else:
            # done, successful or not
            if self._threaded_subprocess.subprocess_returncode == 0:
                # good
                self._set_done()
            else:
                # bad
                self._set_failed()

    def _handle_start(self):
        # clear any existing progress text
        self._progress_text.delete(1.0, tkinter.END)

        # get source_dir field
        source_dir = os.path.abspath(self._source_directory_entry.get())
        if not os.path.exists(source_dir):
            self._set_status_text("Error: input source directory: '%s' does "
                                    "not exist." % source_dir)
            return

        # get be_dir field
        be_dir = os.path.abspath(self._output_directory_entry.get())
        if os.path.exists(be_dir):
            self._set_status_text("Error: bulk_extractor output directory: '%s'"
                                    "already exists." % be_dir)
            return

        # get block size
        try:
            block_size = int(self._block_size_entry.get())
        except ValueError:
            self._set_status_text("Error: invalid block size value: '%s'." %
                                  self._block_size_entry.get())
            return

        # get sector size
        try:
            sector_size = int(self._sector_size_entry.get())
        except ValueError:
            self._set_status_text("Error: invalid sector size value: '%s'." %
                                  self._sector_size_entry.get())
            return

        # get repository name
        repository_name = self._repository_name_entry.get()
        if not repository_name:
            repository_name = source_dir
            self._repository_name_entry.delete(0, tkinter.END)
            self._repository_name_entry.insert(0, repository_name)

        # compose the bulk_extractor import command
        cmd = ["bulk_extractor", "-E", "hashdb",
               "-S", "hashdb_mode=import",
               "-S", "hashdb_block_size=%s" % block_size,
               "-S", "hashdb_import_sector_size=%s" % sector_size,
               "-S", "hashdb_import_repository_name=%s" % repository_name,
               "-o", be_dir,
               "-R", source_dir]

        # start the import
        self._threaded_subprocess = threaded_subprocess.ThreadedSubprocess(
                                                           cmd, self._queue)
        self._threaded_subprocess.start()

        # start the consumer
        self._progress_text.after(200, self._handle_consume_queue)

        self._set_running()

    def _handle_cancel(self):
        self._threaded_subprocess.kill()

    def _handle_close(self):
        exit(0)

