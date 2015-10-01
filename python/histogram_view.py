from colors import background, activebackground
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from offset_selection import OffsetSelection
from histogram_bar import HistogramBar
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramView():
    """Renders the Image Match Histogram view.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, identified_data, filters, offset_selection,
                                       range_selection, fit_range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          offset_selection(OffsetSelection): The selected offset.
          range_selection(RangeSelection): The selected range.
          fit_range_selection(FitRangeSelection): The selected range signal.
        """

        # data variables
        self._range_selection = range_selection

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # add the title
        tkinter.Label(self.frame, text="Image Match Histogram",
                                 bg=background).pack(side=tkinter.TOP, pady=2)

        # add control and legend frame
        control_and_legend_frame = tkinter.Frame(self.frame, height=18+4,
                                                 bg=background)
        control_and_legend_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        # control frame
        control_frame = tkinter.Frame(control_and_legend_frame, bg=background)
        control_frame.place(relx=0.0, anchor=tkinter.NW)

        # button to zoom to fit image
        self._fit_image_icon = tkinter.PhotoImage(file=icon_path("fit_image"))
        fit_image_button = tkinter.Button(control_frame,
                           image=self._fit_image_icon,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        fit_image_button.pack(side=tkinter.LEFT)
        Tooltip(fit_image_button, "Zoom to fit image")

        # button to view annotations
        self._view_annotations_icon = tkinter.PhotoImage(file=icon_path(
                                                        "view_annotations"))
        view_annotations_button = tkinter.Button(control_frame,
                           image=self._view_annotations_icon,
                           command=self._handle_view_annotations,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)

        view_annotations_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(view_annotations_button, "View image annotations\n"
                                         "(CURRENTLY NOT AVAILABLE)")

        # color legend
        legend_frame = tkinter.Frame(control_and_legend_frame, bg=background)
        legend_frame.place(relx=0.5, anchor=tkinter.N)

        # all matches: black
        tkinter.Label(legend_frame, text="   ", background="#333333").pack(
                                                           side=tkinter.LEFT)
        tkinter.Label(legend_frame, text="All matches",
                  background=background).pack(side=tkinter.LEFT, padx=(2,30))

        # ignored matches removed: red
        tkinter.Label(legend_frame, text="   ", background="#660000").pack(
                                                           side=tkinter.LEFT)
        tkinter.Label(legend_frame, text="Ignored matches removed",
                  background=background).pack(side=tkinter.LEFT, padx=(2,30))

        # highlighted matches: green
        tkinter.Label(legend_frame,text="   ", background="#004400").pack(
                                                           side=tkinter.LEFT)
        tkinter.Label(legend_frame,text="Highlighted matches",
                  background=background).pack(side=tkinter.LEFT, padx=(2,0))

        # add the histogram bar
        self._histogram_bar = HistogramBar(self.frame, identified_data,
                                    filters, offset_selection,
                                    range_selection, fit_range_selection)
        self._histogram_bar.frame.pack(side=tkinter.TOP)

        # set command for fit_image_button
        fit_image_button.configure(command=self._histogram_bar.fit_image)

    def _handle_view_annotations(self):
        print("view annotations TBD")

