import tkinter 
from forensic_path import offset_string

class ProjectSummaryView():
    """Provides a frame that prints a brief summary of the opened project
    from fields in identified data.

    Attributes:
      frame(Frame): the containing frame for the identified data summary
      view.
    """

    def __init__(self, master, identified_data):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
        """
        self._identified_data = identified_data

        # make the containing frame
        self.frame = tkinter.Frame(master)

        # title
        tkinter.Label(self.frame, text="Project").pack(side=tkinter.TOP,
                                                               pady=(0,4))

        # media image
        self._image_text = tkinter.Label(self.frame)
        self._image_text.pack(side=tkinter.TOP, anchor="w")

        # media image size
        self._image_size_text = tkinter.Label(self.frame)
        self._image_size_text.pack(side=tkinter.TOP, anchor="w")

        # hashdb database path
        self._database_text = tkinter.Label(self.frame)
        self._database_text.pack(side=tkinter.TOP, anchor="w")

        # register to receive identified_data change events
        identified_data.set_callback(self._handle_identified_data_change)

        # set initial state
        self._handle_identified_data_change()

    # this function is registered to and called by IdentifiedData
    def _handle_identified_data_change(self, *args):
        if self._identified_data.image_filename:
            # identified_data opened
            self._image_text["text"] = 'Image: %s' % \
                               self._identified_data.image_filename
            self._image_size_text["text"] = 'Image size: %s' % \
                               offset_string(self._identified_data.image_size)
            self._database_text["text"] = 'Database: %s' % \
                               self._identified_data.hashdb_dir
        else:
            # identified_data not opened
            self._image_text["text"] = 'Image: Not opened'
            self._image_size_text["text"] = 'Image size: Not opened'
            self._database_text["text"] = 'Database: Not opened'

