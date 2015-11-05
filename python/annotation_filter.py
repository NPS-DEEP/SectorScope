try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class AnnotationFilter():
    """Contains the set of annotation types to ignore.

    Call fire_change after changing state to alert callbacks.

    Attributes:
      ignored_types(str): Annotation types to ignore.

    Requirement:
      Tk must be initialized for tkinter.Variable to work.
    """

    ignored_types = set()

    def __init__(self):
        # the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        self._annotation_filter_changed = tkinter.BooleanVar()

    def set(self, ignored_types):
        """set ignored_types to the set of ignored types provided."""
        self.ignored_types = ignored_types
        self._annotation_filter_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on filter change."""
        self._annotation_filter_changed.trace_variable('w', f)

