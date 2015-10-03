from fit_range_selection import FitRangeSelection
from image_hex_window import ImageHexWindow
from colors import background, activebackground
from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
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

    def __init__(self, master, identified_data, filters, range_selection):
        """Args:
          master(a UI container): Parent.
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters that impact the view.
          range_selection(RangeSelection): The selected range.
        """

        # data variables
        self._range_selection = range_selection

        # the image hex window that the show hex view button can show
        self._image_hex_window = ImageHexWindow(master, identified_data,
                                                  filters, range_selection)

        # the fit byte range selection signal manager
        fit_range_selection = FitRangeSelection()

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=background)

        # add the title
        tkinter.Label(self.frame, text="Image Match Histogram",
                                 bg=background).pack(side=tkinter.TOP, pady=2)

        # add button and legend frame
        button_and_legend_frame = tkinter.Frame(self.frame, bg=background)
        button_and_legend_frame.pack(side=tkinter.TOP, fill=tkinter.X)

        # button frame
        button_frame = tkinter.Frame(button_and_legend_frame, bg=background)
        button_frame.pack(side=tkinter.LEFT)

        # button to zoom to fit image
        self._fit_image_icon = tkinter.PhotoImage(file=icon_path("fit_image"))
        fit_image_button = tkinter.Button(button_frame,
                           image=self._fit_image_icon,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)
        fit_image_button.pack(side=tkinter.LEFT)
        Tooltip(fit_image_button, "Zoom to fit image")

        # button to zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(button_frame,
                              image=self._fit_range_icon,
                              command=fit_range_selection.fire_change,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        self._fit_range_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(self._fit_range_button, "Zoom to range")
 
        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        show_hex_view_button = tkinter.Button(button_frame,
                              image=self._show_hex_view_icon,
                              command=self._image_hex_window.show,
                              bg=background, activebackground=activebackground,
                              highlightthickness=0)
        show_hex_view_button.pack(side=tkinter.LEFT)
        Tooltip(show_hex_view_button, "Show hex view of selection")

        # button to view annotations
        self._view_annotations_icon = tkinter.PhotoImage(file=icon_path(
                                                        "view_annotations"))
        view_annotations_button = tkinter.Button(button_frame,
                           image=self._view_annotations_icon,
                           command=self._handle_view_annotations,
                           bg=background, activebackground=activebackground,
                           highlightthickness=0)

        view_annotations_button.pack(side=tkinter.LEFT, padx=4)
        Tooltip(view_annotations_button, "Manage image annotations\n"
                                         "(CURRENTLY NOT AVAILABLE)")

        # color legend
        legend_frame = tkinter.Frame(button_and_legend_frame, bg=background)
        legend_frame.pack(side=tkinter.LEFT, padx=(40,0))

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
                                    filters,
                                    range_selection, fit_range_selection)
        self._histogram_bar.frame.pack(side=tkinter.TOP)

        # set command for fit_image_button
        fit_image_button.configure(command=self._histogram_bar.fit_image)

        # register to receive range selection change events
        range_selection.set_callback(self._handle_range_selection_change)

        # set to basic initial state
        self._handle_range_selection_change()

    def _handle_view_annotations(self):
        print("view annotations TBD")

    # this function is registered to and called by RangeSelection
    def _handle_range_selection_change(self, *args):
        if self._range_selection.is_selected:
            # enable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.NORMAL)

        else:
            # disable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.DISABLED)

