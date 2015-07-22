import tkinter 
from forensic_path import offset_string

class IdentifiedDataSummaryView():
    """Provides a frame that prints a brief summary of the identified data.

    Attributes:
      frame(Frame): the containing frame for the identified data summary
      view.
    """

    def __init__(self, master, identified_data):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
        """

        # make the containing frame
        self.frame = tkinter.Frame(master)

        tkinter.Label(self.frame,
                      text='Image: %s' % identified_data.image_filename) \
                          .pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(self.frame, text='Image size: %s ' %
                          offset_string(identified_data.image_size)) \
                          .pack(side=tkinter.TOP, anchor="w")
        tkinter.Label(self.frame,
                      text='Database: %s'%identified_data.hashdb_dir) \
                          .pack(side=tkinter.TOP, anchor="w")

