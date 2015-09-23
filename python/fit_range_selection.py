import tkinter

class FitRangeSelection():
    """Manage a byte offset fit range selection event.

    Registered callbacks are called when fit_range is set or cleared.

    _fit_range_selection_changed is used as a signal.
    Its value is always true.

    Rationale:
      Signaling a fit range selection request avoids layering issues
      that would be required by a call chain between the fit_range button
      and the histogram_bar widget.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._fit_range_selection_changed = tkinter.BooleanVar()

    def fire_change(self):
        # signal change
        self._fit_range_selection_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on range selection change."""
        self._fit_range_selection_changed.trace_variable('w', f)

