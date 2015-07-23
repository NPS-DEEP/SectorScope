import tkinter

class Filters():
    """Contains the filters to apply to the filtered view.

    Attributes:
      max_hashes (int): Maximum duplicates allowed before disregarding the hash.
      filter_flagged_blocks (bool): Whether to filter flagged hashes.
      filtered_sources (array<int>): Sectors to filter.
      filtered_hashes (array<str>): Hashes to filter.

    Requirement:
      Tk must be initialized before Filters for tkinter.Variable to work.
    """

    def __init__(self):
        # filters
        self.max_hashes = 0
        self.filter_flagged_blocks = True
        self.filtered_sources = []
        self.filtered_hashes = []

        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._filter_changed = tkinter.BooleanVar()

    """Call this function to alert that the filter changed."""
    def fire_change(self):
        print("filters.fire.a")
        # _filter_changed is only used as a signal.  Its value is always true.
        self._filter_changed.set(True)
        print("filters.fire.b")

    """Register function f to be called on filter change."""
    def set_callback(self, f):
        self._filter_changed.trace_variable('w', f)

