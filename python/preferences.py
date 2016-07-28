import colors
from icon_path import icon_path
from tooltip import Tooltip
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class Preferences():
    """Manages preference settings.  Changes call callbacks.

    Preferences that modules may be interested in controlling:
      offset_format(str): The format that the user wants for seeing
        media image offsets, one of "hex", "decimal", or "sector".
      auto_y_scale(bool): Whether the Y-axis of the histogram bar will
        auto-scale.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._preferences_changed = tkinter.BooleanVar()

        self.offset_format = "sector"
        self.auto_y_scale = True


    def reset(self):
        self.offset_format = "sector"
        self.auto_y_scale = True
        self._fire_change()

    def set_next_offset_format(self):
        if self.offset_format == "sector":
            self.offset_format = "decimal"
        elif self.offset_format == "decimal":
            self.offset_format = "hex"
        elif self.offset_format == "hex":
            self.offset_format = "sector"
        else:
            raise RuntimeError("program error")
        self._fire_change()

    def set_toggle_auto_y_scale(self):
        self.auto_y_scale = not self.auto_y_scale
        self._fire_change()

    def set_callback(self, f):
        """Register function f to be called on bar scale change."""
        self._preferences_changed.trace_variable('w', f)

    def _fire_change(self):
        """Call this function to alert that the scale changed."""
        # _preferences_changed is used as a signal.  Its value is always true.
        self._preferences_changed.set(True)

