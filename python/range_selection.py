import tkinter

class RangeSelection():
    """Manage a byte offset range selection.

    Registered callbacks are called when range is set or cleared.

    _range_selection_changed is used as a signal.
    Its value is always true.

    Attributes:
      is_selected(bool): Whether a range is selected.
      start_offset(int): Start offset of range.
      stop_offset(int): Start offset of range.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    is_selected = False
    start_offset = 0
    stop_offset = 0

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._range_selection_changed = tkinter.BooleanVar()

    def set(self, offset1, offset2):
        """Set offsets.  Input can be out of order."""
        if offset1 < offset2:
            self.start_offset = offset1
            self.stop_offset = offset2
        else:
            self.start_offset = offset2
            self.stop_offset = offset1
        self.is_selected = True

        # signal change
        self._range_selection_changed.set(True)

    def clear(self):
        self.is_selected = False
        self.start_offset = 0
        self.stop_offset = 0
        
        # signal change
        self._range_selection_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on range selection change."""
        self._range_selection_changed.trace_variable('w', f)

