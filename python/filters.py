import tkinter

class Filters():
    """Contains the filters to apply to the filtered view.

    Attributes:
      max_hashes (int): Maximum duplicates allowed before disregarding the hash.
      filter_flagged_blocks (bool): Whether to filter flagged hashes.
      skipped_sources (array<int>): Sectors to skip.
      skipped_hashes (array<str>): Hashes to skip.

    Requirement:
      Tk must be initialized before Filters for tkinter.Variable to work.
    """

    def __init__(self):
        # filters
        self.max_hashes = 0
        self.filter_flagged_blocks = True
        self.skipped_sources = []
        self.skipped_hashes = []

        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._filter_changed = tkinter.BooleanVar()

    """Call this function to alert that the filter changed."""
    def fire_change(self):
        print("filters.fire.a")
        self._filter_changed.set(True)
        print("filters.fire.b")

    """Register function f to be called on filter change."""
    def set_callback(self, f):
        self._filter_changed.trace_variable('w', f)

