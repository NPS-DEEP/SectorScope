import tkinter

class Filters():
    """Contains the filters to apply to the filtered view.

    Registered callbacks are called when cleared.
    Call fire_change after changing filter state to alert callbacks.

    Attributes:
      max_hashes (int): Maximum duplicates allowed before disregarding the hash.
      filter_flagged_blocks (bool): Whether to filter flagged hashes.
      filtered_sources (array<int>): Sectors to filter.
      filtered_hashes (array<str>): Hashes to filter.

    Requirement:
      Tk must be initialized before Filters for tkinter.Variable to work.
    """

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._filter_changed = tkinter.BooleanVar()

        # initialize the filters
        self.clear()

    def clear(self):
        """Clear but do not fire change."""
        # filters
        self.max_hashes = 0
        self.filter_flagged_blocks = True
        self.filtered_sources = []
        self.filtered_hashes = []
        self.fire_change()

    def fire_change(self):
        """Call this function to alert that the filter changed."""
        # _filter_changed is used as a signal.  Its value is always true.
        self._filter_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on filter change."""
        self._filter_changed.trace_variable('w', f)

