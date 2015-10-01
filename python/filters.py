try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class Filters():
    """Contains all highlight and ignore variables used for filtering.

    Registered callbacks are called when cleared.
    Call fire_change after changing filter state to alert callbacks.

    Attributes:
      ignore_max_hashes (int): Maximum duplicates allowed before ignoring
        the hash.
      ignore_flagged_blocks (bool): Whether to highlight flagged hashes.
      ignored_sources (set<int>): Sectors to ignore.
      ignored_hashes (set<str>): Hashes to ignore.
      highlighted_sources (set<int>): Sectors to highlight.
      highlighted_hashes (set<str>): Hashes to highlight.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    ignore_max_hashes = None
    ignored_sources = set()
    ignored_hashes = set()
    highlighted_sources = set()
    highlighted_hashes = set()

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._filter_changed = tkinter.BooleanVar()

        # initialize the highlights data elements
        self.clear()

    def clear(self):
        """Clear but do not fire change."""
        # ignored
        self.ignore_max_hashes = 0
        self.ignore_flagged_blocks = True
        self.ignored_sources.clear()
        self.ignored_hashes.clear()
        self.highlighted_sources.clear()
        self.highlighted_hashes.clear()

    def fire_change(self):
        """Call this function to alert that filtering changed."""
        # _filter_changed is used as a signal.  Its value is always true.
        self._filter_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on filter change."""
        self._filter_changed.trace_variable('w', f)

