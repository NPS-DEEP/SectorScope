import tkinter 
from forensic_path import offset_string

class SettingsView():
    """Provides a frame that prints and manages settings.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data,
                 max_hashes_trace_var, skip_flagged_blocks_trace_var):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          max_hashes_trace_var(IntVar): Variable to communicate the
            maximum hashes allowed setting.
        """

        # define the selection variables
        self._max_hashes_trace_var = max_hashes_trace_var

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # make the settings and the sources frames

        # make the settings frame on the left
#        settings_frame = tkinter.Frame(self.frame, relief=tkinter.SOLID, borderwidth=1)
        settings_frame = tkinter.Frame(self.frame)
        settings_frame.pack(side=tkinter.LEFT, padx=8, pady=8)

        # put max hashes above in settings_frame
        max_hashes_frame = tkinter.Frame(settings_frame)
        max_hashes_frame.pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(max_hashes_frame, text="Max Same Hashes:") \
                                        .pack(side=tkinter.LEFT, anchor="w")
        self.max_hashes_entry = tkinter.Entry(max_hashes_frame, width=6)
        self.max_hashes_entry.insert(0, "None")
        self.max_hashes_entry.pack(side=tkinter.LEFT, anchor="w")
        self.max_hashes_entry.bind('<Return>',
                                   self._handle_max_hashes_selection)
        self.max_hashes_entry.bind('<FocusOut>',
                                   self._handle_max_hashes_selection)

        # make the sources frame to the right
        sources_frame = tkinter.Frame(self.frame)
        sources_frame.pack(side=tkinter.LEFT, padx=40)
        tkinter.Label(sources_frame,
                      text='Image: %s' % identified_data.image_filename) \
                          .pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(sources_frame, text='Image size: %s ' %
                          offset_string(identified_data.image_size)) \
                          .pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(sources_frame,
                      text='Database: %s'%identified_data.hashdb_dir) \
                          .pack(side=tkinter.TOP, anchor="w")

    def _handle_max_hashes_selection(self, e):
        # get max_hashes int
        try:
            max_hashes = int(self.max_hashes_entry.get())
        except ValueError:
            max_hashes = 0

        # set entry to make sure it looks nice
        self.max_hashes_entry.delete(0, tkinter.END)
        if max_hashes == 0:
            self.max_hashes_entry.insert(0, "None")
        else:
            self.max_hashes_entry.insert(0, "%s"%max_hashes)

        # only set the trace variable if it changes
        if (max_hashes != self._max_hashes_trace_var.get()):
            self._max_hashes_trace_var.set(max_hashes)

