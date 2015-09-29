try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

# Code Adapted from http://effbot.org/zone/tkinter-autoscrollbar.htm.
"""Scrollbar that is only visible when scrollregion > window."""
class AutoScrollbar(tkinter.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tkinter.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        print("warn:  cannot use pack with this widget")
        raise RuntimeError("cannot use pack with this widget")
    def place(self, **kw):
        print("warn: cannot use place with this widget")
        raise RuntimeError("cannot use place with this widget")
