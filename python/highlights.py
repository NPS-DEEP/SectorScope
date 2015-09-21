import tkinter

class Highlights():
    """Contains all highlight variables used for specifying highlighting.

    Registered callbacks are called when cleared.
    Call fire_change after changing highlight state to alert callbacks.

    Attributes:
      max_hashes (int): Maximum duplicates allowed before disregarding the hash.
      highlight_flagged_blocks (bool): Whether to highlight flagged hashes.
      highlighted_sources (set<int>): Sectors to highlight.
      highlighted_hashes (set<str>): Hashes to highlight.

    Requirement:
      Tk must be initialized before Highlights for tkinter.Variable to work.
    """

    highlighted_sources = set()
    highlighted_hashes = set()

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._highlight_changed = tkinter.BooleanVar()

        # initialize the highlights data elements
        self.clear()

    def clear(self):
        """Clear but do not fire change."""
        # highlights
        self.max_hashes = 0
        self.highlight_flagged_blocks = True
        self.highlighted_sources.clear()
        self.highlighted_hashes.clear()
        self.fire_change()

    def fire_change(self):
        """Call this function to alert that highlighting changed."""
        # _highlight_changed is used as a signal.  Its value is always true.
        self._highlight_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on highlight change."""
        self._highlight_changed.trace_variable('w', f)

