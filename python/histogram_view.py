from fit_range_selection import FitRangeSelection
from media_hex_window import MediaHexWindow
import colors
from icon_path import icon_path
from tooltip import Tooltip
from histogram_bar import HistogramBar
from annotation_window import AnnotationWindow
from media_export_window import MediaExportWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramView():
    """Renders the Media Image Match Histogram view.

    Attributes:
      frame(Frame): the containing frame for this view.
    """

    def __init__(self, master, data_manager, annotation_filter,
                 preferences, histogram_control):
        """Args:
          master(a UI container): Parent.
          data_manager(DataManager): Manages scan data and filters.
          annotation_filter(AnnotationFilter): The annotation selection filter.
          preferences(Preferences): Includes the offset format preference.
          histogram_control(HistogramControl): Interfaces for controlling
            the histogram view.
        """

        self._master = master
        self._data_manager = data_manager

        # preferences
        self._preferences = preferences

        # histogram control
        self._histogram_control = histogram_control

        # the media hex window that the show hex view button can show
        self._media_hex_window = MediaHexWindow(master, data_manager,
                                                histogram_control)

        # the fit byte range selection signal manager
        fit_range_selection = FitRangeSelection()

        # the annotation window
        self._annotation_window = AnnotationWindow(master, data_manager,
                                                          annotation_filter)

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # add controls frame
        controls_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        controls_frame.pack(side=tkinter.TOP, anchor="w")

        # button to zoom to fit media image
        self._fit_media_icon = tkinter.PhotoImage(file=icon_path("fit_media"))
        self._fit_media_button = tkinter.Button(controls_frame,
                           image=self._fit_media_icon,
                           command=self._handle_fit_media,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._fit_media_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(self._fit_media_button, "Zoom to fit media image")

        # button to zoom to fit range
        self._fit_range_icon = tkinter.PhotoImage(file=icon_path("fit_range"))
        self._fit_range_button = tkinter.Button(controls_frame,
                              image=self._fit_range_icon,
                              command=fit_range_selection.fire_change,
                              bg=colors.BACKGROUND,
                              activebackground=colors.ACTIVEBACKGROUND,
                              highlightthickness=0)
        self._fit_range_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(self._fit_range_button, "Zoom to range")

        # button to show hex view for selection
        self._show_hex_view_icon = tkinter.PhotoImage(file=icon_path(
                                                              "show_hex_view"))
        show_hex_view_button = tkinter.Button(controls_frame,
                              image=self._show_hex_view_icon,
                              command=self._media_hex_window.show,
                              bg=colors.BACKGROUND,
                              activebackground=colors.ACTIVEBACKGROUND,
                              highlightthickness=0)
        show_hex_view_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(show_hex_view_button, "Show hex view of block under cursor")

        # button to open window to export bytes to file
        self._show_export_window_icon = tkinter.PhotoImage(file=icon_path(
                                                        "show_export_window"))
        show_export_window_button = tkinter.Button(controls_frame,
                              image=self._show_export_window_icon,
                              command=self._handle_export_window,
                              bg=colors.BACKGROUND,
                              activebackground=colors.ACTIVEBACKGROUND,
                              highlightthickness=0)
        show_export_window_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(show_export_window_button, "Export media range to file")

        # button to view annotations
        self._view_annotations_icon = tkinter.PhotoImage(file=icon_path(
                                                        "view_annotations"))
        view_annotations_button = tkinter.Button(controls_frame,
                           image=self._view_annotations_icon,
                           command=self._handle_view_annotations,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)

        view_annotations_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(view_annotations_button, "Manage annotations shown")

        # button to toggle offset_format_preference
        self._offset_format_preference_icon = tkinter.PhotoImage(
                                file=icon_path("offset_format_preference"))
        offset_format_preference_button = tkinter.Button(controls_frame,
                       image=self._offset_format_preference_icon,
                       command=self._handle_offset_format_preference,
                       bg=colors.BACKGROUND,
                       activebackground=colors.ACTIVEBACKGROUND,
                       highlightthickness=0)
        offset_format_preference_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(offset_format_preference_button,
                  "Toggle offset format between\nsector, decimal, and hex")

        # button to toggle auto_y_scale_preference
        self._auto_y_scale_preference_icon = tkinter.PhotoImage(file=icon_path(
                                                  "auto_y_scale_preference"))
        auto_y_scale_preference_button = tkinter.Button(controls_frame,
                           image=self._auto_y_scale_preference_icon,
                           command=self._handle_auto_y_scale_preference,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)

        auto_y_scale_preference_button.pack(side=tkinter.LEFT, padx=2)
        Tooltip(auto_y_scale_preference_button,
                "Disable/enable auto-Y-axis\nhistogram bar scale")

        # range selection
        range_selection_frame = tkinter.Frame(self.frame, bg=colors.BACKGROUND)
        range_selection_frame.pack(side=tkinter.TOP, anchor="w")

        # add the histogram bar
        self._histogram_bar = HistogramBar(self.frame, data_manager,
                                    fit_range_selection,
                                    preferences, annotation_filter,
                                    histogram_control)
        self._histogram_bar.frame.pack(side=tkinter.TOP)

        # register to receive histogram_control change events
        histogram_control.set_callback(self._handle_histogram_control_change)

        # set to basic initial state
        self._handle_histogram_control_change()

    def _handle_fit_media(self):
        self._histogram_control.fit_media()

    def _handle_view_annotations(self):
        self._annotation_window.show()

    def _handle_export_window(self):
        MediaExportWindow(self._master, self._data_manager)

    def _handle_offset_format_preference(self):
        self._preferences.set_next_offset_format()

    def _handle_auto_y_scale_preference(self):
        self._preferences.set_toggle_auto_y_scale()

    # this function is registered to and called by RangeSelection
    def _handle_histogram_control_change(self, *args):
        if self._histogram_control.is_valid_range:
            # enable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.NORMAL)

        else:
            # disable button to zoom to fit range
            self._fit_range_button.config(state=tkinter.DISABLED)

