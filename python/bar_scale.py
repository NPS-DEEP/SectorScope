import colors
from icon_path import icon_path
from tooltip import Tooltip
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class BarScale():
    """Provides the scale value used for scaling the histogram bar height
      and interfaces to change it.  Changes call callbacks.

    Attributes:
      scale(int): The scale to apply to the histogram bar height.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    MAX = 10000
    scale = 1

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._bar_scale_changed = tkinter.BooleanVar()

    def reset(self):
        self.scale = 1
        self._fire_change()

    def plus(self):
        if self.scale >= 10:
            self.scale //= 10
            self._fire_change()
    
    def minus(self):
        if self.scale <= self.MAX:
            self.scale *= 10
            self._fire_change()

    def set_callback(self, f):
        """Register function f to be called on bar scale change."""
        self._bar_scale_changed.trace_variable('w', f)

    def _fire_change(self):
        """Call this function to alert that the scale changed."""
        # _bar_scale_changed is used as a signal.  Its value is always true.
        self._bar_scale_changed.set(True)

