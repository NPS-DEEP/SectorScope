import tkinter 
from forensic_path import offset_string

class FilterView():
    """Provides a frame containing user selecton controlled filters.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, filters):
        """Args:
          master(a UI container): Parent.
          filters(Filters): Filters that filter hashes and sources.
        """

        # filters
        self._filters = filters

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # put in the filter title
        tkinter.Label(self.frame, text="Filters:") \
                          .pack(side=tkinter.TOP, anchor="w")

        # put max hashes above
        max_hashes_frame = tkinter.Frame(self.frame)
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

        # set up the local checkbutton trace var so change function gets called
        self._filter_flagged_blocks_trace_var = tkinter.IntVar()
        self._filter_flagged_blocks_trace_var.set(filters.filter_flagged_blocks)
        self._filter_flagged_blocks_trace_var.trace_variable('w',
                               self._handle_filter_flagged_blocks_selection)

        # put filter_flagged_blocks checkbutton below
        self.filter_flagged_blocks_checkbutton = tkinter.Checkbutton(
                           self.frame, text="Filter Flagged Blocks",
                           variable=self._filter_flagged_blocks_trace_var,
                           bd=0,padx=0,pady=0)
        self.filter_flagged_blocks_checkbutton.pack(side=tkinter.TOP,
                                                    anchor="w")

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

        # only set if max_hashes changes
        if max_hashes != self._filters.max_hashes:
            self._filters.max_hashes = max_hashes
            self._filters.fire_change()

    def _handle_filter_flagged_blocks_selection(self, *args):
        self._filters.filter_flagged_blocks = \
                              self._filter_flagged_blocks_trace_var.get()
        self._filters.fire_change()

