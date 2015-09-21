import tkinter 
from sys import platform

class HistogramPan():
    """Provides right-click pan capability for the histogram bar.
      Note difference for Mac."""

    # pan state
    _pan_down_x = None
    _pan_down_start_offset = None

    def __init__(self, histogram_bar, pan_widget):

        """Args:
          histogram_bar(<widget>): The widget responsive to right-click pan.
        """
        self._histogram_bar = histogram_bar

        # bind control mouse events
        if platform == 'darwin':
            # mac right-click is Button-2
            pan_widget.bind('<Button-2>', self._handle_pan_press, add='+')
            pan_widget.bind('<B2-Motion>', self._handle_pan_move, add='+')
        else:
            # Linux, Win right-click is Button-3
            pan_widget.bind('<Button-3>', self._handle_pan_press, add='+')
            pan_widget.bind('<B3-Motion>', self._handle_pan_move, add='+')
 
    def _handle_pan_press(self, e):
        self._pan_down_x = e.x
        self._pan_down_start_offset = self._histogram_bar.start_offset

    def _handle_pan_move(self, e):
        self._histogram_bar.pan(self._pan_down_start_offset,
                                                      self._pan_down_x - e.x)

