import colors
from icon_path import icon_path
from tooltip import Tooltip
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class Preferences():
    """Manages preference settings.  Changes call callbacks.

    Attributes:
      offset_format(str): one of "hex", "decimal", or "byte alignment".

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    offset_format = "hex"

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._preferences_changed = tkinter.BooleanVar()

    def reset(self):
        self.offset_format = "hex"
        self._fire_change()

    def set_next(self):
        if self.offset_format == "hex":
            self.offset_format = "decimal"
        elif self.offset_format == "decimal":
            self.offset_format = "byte alignment"
        elif self.offset_format == "byte alignment":
            self.offset_format = "hex"
        else:
            raise RuntimeError("program error")
        self._fire_change()

    def set_callback(self, f):
        """Register function f to be called on bar scale change."""
        self._preferences_changed.trace_variable('w', f)

    def _fire_change(self):
        """Call this function to alert that the scale changed."""
        # _preferences_changed is used as a signal.  Its value is always true.
        self._preferences_changed.set(True)

