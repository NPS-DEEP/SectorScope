import colors
from icon_path import icon_path
from tooltip import Tooltip
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class BarScaleView():
    """Provides a frame of controls for scaling the histogram bar height.

    Attributes:
      frame(Frame): The containing frame for this view.
    """

    scale = 1

    def __init__(self, master, bar_scale):
        """Args:
          master(a UI container): Parent.
        """

        self._bar_scale = bar_scale

        # make the containing frame
        self.frame = tkinter.Frame(master, bg=colors.BACKGROUND)

        # add the + button
        self._plus_icon = tkinter.PhotoImage(file=icon_path("y_plus"))
        self._plus_button = tkinter.Button(self.frame,
                           image=self._plus_icon,
                           command=bar_scale.plus,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._plus_button.pack(side=tkinter.LEFT)
        Tooltip(self._plus_button, "Increase bar height")

        # add the - button
        self._minus_icon = tkinter.PhotoImage(file=icon_path("y_minus"))
        self._minus_button = tkinter.Button(self.frame,
                           image=self._minus_icon,
                           command=bar_scale.minus,
                           bg=colors.BACKGROUND,
                           activebackground=colors.ACTIVEBACKGROUND,
                           highlightthickness=0)
        self._minus_button.pack(side=tkinter.LEFT)
        Tooltip(self._minus_button, "Decrease bar height")

        # add the scale value label
        self._scale_value_label = tkinter.Label(self.frame,
                         width=10, anchor="w",
                         bg=colors.BACKGROUND)
        self._scale_value_label.pack(side=tkinter.TOP, pady=2)

        # register to receive bar height scale change events
        bar_scale.set_callback(self._handle_bar_scale_change)

        # show initial scale
        self._show()

    def _show(self):
        self._scale_value_label["text"] = "1:%s" % self._bar_scale.scale
        # disable + button if not useful
        if self._bar_scale.scale == 1:
            self._plus_button.config(state=tkinter.DISABLED)
        else:
            self._plus_button.config(state=tkinter.NORMAL)

        # disable - button if not useful
        if self._bar_scale.scale == self._bar_scale.MAX:
            self._minus_button.config(state=tkinter.DISABLED)
        else:
            self._minus_button.config(state=tkinter.NORMAL)

    # this function is registered to and called by BarHeight
    def _handle_bar_scale_change(self, *args):
        self._show()


    # this function is registered to and called by BarHeight
    def _handle_bar_scale_change(self, *args):
        self._show()

