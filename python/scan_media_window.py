# Use this to scan for hashes.
# Relative paths are replaced with absolute paths.

import os
import sys
import command_runner
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

class ScanMediaWindow():
    """Scan a media image for matching hashes using a GUI interface.
    """

    def __init__(self, master, media="", hashdb_dir="", output_file="",
                 step_size=512):

        """Args:
          media(str): The media image to scan.
          hashdb_dir(str): Path to the hashdb directory to scan against.
          output_file(str): The new output file to create during the scan.
          step_size(int): The step size to increment along while scanning.
        """
        # input parameters
        self._media = media
        self._hashdb_dir = hashdb_dir
        self._output_file = output_file
        self._step_size = step_size

        # the queue for import text
        self._queue = queue.Queue()

        # toplevel
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title("SectorScope Scan Media Image")

        # make the control frame
        control_frame = tkinter.Frame(self._root_window, borderwidth=1,
                                      relief=tkinter.RIDGE)
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
        button_frame = self._make_button_frame(self._root_window)
        button_frame.pack(side=tkinter.TOP, padx=8, pady=8)

    def _make_required_frame(self, master):
        required_frame = tkinter.LabelFrame(master,
                                            text="Required Parameters",
                                            padx=8, pady=8)

        # media label
        tkinter.Label(required_frame, text="Media Image") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # media entry
        self._media_entry = tkinter.Entry(required_frame, width=40)
        self._media_entry.grid(row=0, column=1, sticky=tkinter.W,
                                          padx=8)
        self._media_entry.insert(0, self._media)

        # media image chooser button
        media_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_media_chooser)
        media_entry_button.grid(row=0, column=2, sticky=tkinter.W)

        # hashdb database directory label
        tkinter.Label(required_frame, text="Hash Database") \
                          .grid(row=1, column=0, sticky=tkinter.W)

        # hashdb directory input entry
        self._hashdb_directory_entry = tkinter.Entry(required_frame, width=40)
        self._hashdb_directory_entry.grid(row=1, column=1, sticky=tkinter.W,
                                          padx=8)
        self._hashdb_directory_entry.insert(0, self._hashdb_dir)

        # hashdb directory chooser button
        hashdb_directory_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_hashdb_directory_chooser)
        hashdb_directory_entry_button.grid(row=1, column=2, sticky=tkinter.W)

        # output_file label
        tkinter.Label(required_frame, text="Scan Output File") \
                          .grid(row=2, column=0, sticky=tkinter.W)

        # output_file input entry
        self._output_file_entry = tkinter.Entry(required_frame, width=40)
        self._output_file_entry.grid(row=2, column=1, sticky=tkinter.W,
                                          padx=8)
        self._output_file_entry.insert(0, self._output_file)

        # output_file chooser button
        output_file_entry_button = tkinter.Button(required_frame,
                                text="...",
                                command=self._handle_output_file_chooser)
        output_file_entry_button.grid(row=2, column=2, sticky=tkinter.W)

        return required_frame

    def _make_optional_frame(self, master):
        optional_frame = tkinter.LabelFrame(master,
                                            text="Options",
                                            padx=8, pady=8)

        # step size label
        tkinter.Label(optional_frame, text="Step Size") \
                          .grid(row=0, column=0, sticky=tkinter.W)

        # step size entry
        self._step_size_entry = tkinter.Entry(optional_frame, width=8)
        self._step_size_entry.grid(row=0, column=1, sticky=tkinter.W, padx=8)
        self._step_size_entry.insert(0, self._step_size)

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
        self._progress_text.see(tkinter.END)

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

    def _handle_media_chooser(self, *args):
        media_file = fd.askopenfilename(title="Open Media Image")
        if media_file:
            self._media_entry.delete(0, tkinter.END)
            self._media_entry.insert(0, media_file)

    def _handle_hashdb_directory_chooser(self, *args):
        hashdb_directory = fd.askdirectory(
                               title="Open hashdb Database Directory",
                               mustexist=True)
        if hashdb_directory:
            self._hashdb_directory_entry.delete(0, tkinter.END)
            self._hashdb_directory_entry.insert(0, hashdb_directory)

    def _handle_output_file_chooser(self, *args):
        file_opt={"title":"Open Output File", "defaultextension":".json"}
        output_file = fd.asksaveasfilename(**file_opt)
        if output_file:
            self._output_file_entry.delete(0, tkinter.END)
            self._output_file_entry.insert(0, output_file)

    def _handle_consume_queue(self):
        is_done = self._command_runner.is_done()

        # consume the queue
        while not self._queue.empty():
            name, line = self._queue.get()

            # stderr and stdout lines go to output_file
            if name == "stderr" or name == "stdout":
                self._outfile.write(line)

            # report all but non-comment lines from stdout
            if name != "stdout" or len(line) > 0 and line[0] == '#':
                self._progress_text.insert(tkinter.END, "%s: %s" %(name, line))
                self._progress_text.see(tkinter.END)

        # more or done
        if not is_done:
            # keep progress_text consuming queue
            self._progress_text.after(200, self._handle_consume_queue)
        else:
            # done, successful or not
            # close outfile
            self._outfile.close()

            # show status
            if self._command_runner.return_code() == 0:
                # good
                self._set_done()
            else:
                # bad
                self._set_failed()

    def _handle_start(self):
        # clear any existing progress text
        self._progress_text.delete(1.0, tkinter.END)

        # get media filename field
        media = os.path.abspath(self._media_entry.get())
        if not os.path.exists(media):
            self._set_status_text("Error: media image '%s' does "
                                    "not exist." % media)
            return

        # get hashdb_dir field
        hashdb_dir = os.path.abspath(self._hashdb_directory_entry.get())
        if not os.path.exists(hashdb_dir):
            self._set_status_text("Error: hashdb database directory '%s' "
                                    "does not exist." % hashdb_dir)
            return

        # get output_file field
        output_file = os.path.abspath(self._output_file_entry.get())
        if os.path.exists(output_file):
            self._set_status_text("Error: output file '%s' "
                                    "already exists." % output_file)
            return

        # get step size
        try:
            step_size = int(self._step_size_entry.get())
        except ValueError:
            self._set_status_text("Error: invalid step size value: '%s'." %
                                  self._step_size_entry.get())
            return

        # compose the scan_media command
        cmd = ["hashdb", "scan_media", "-s", "%d"%step_size, hashdb_dir, media]

        # open the output file, it is closed when _handle_consume_queue stops
        try:
            self._outfile = open(output_file, 'w')
        except Exception as e:
            self._queue.put(("Error", "Unable to open %s.  Aborting." % self._outfilename))
            return

        # start the scan
        self._command_runner = command_runner.CommandRunner(cmd, self._queue)

        # start the consumer
        self._progress_text.after(200, self._handle_consume_queue)

        self._set_running()

    def _handle_cancel(self):
        self._command_runner.kill()

    def _handle_close(self):
        self._root_window.destroy()

