import tkinter 
from auto_scrollbar import AutoScrollbar

class ScrolledCanvas():
    """A canvas providing a frame that can be scrolled.

    Attributes:
    scrolled_frame(Frame): The scrollable frame to be populated with
      widgets to be scrolled.
    """

    def __init__(self, master, *, canvas_width=300, canvas_height=200,
                                  frame_width=300, frame_height=200):
        """Args:
          master(a UI container): Parent.
          canvas_width, canvas_height(int): initial size of canvas.
          frame_width, frame_height(int): constant size of frame.  Do not
            call pack on scrolled_frame or its widgets will get wired to
            resize when the canvas is resized.
        """

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        root_xscrollbar = AutoScrollbar(master, orient=tkinter.HORIZONTAL)
        root_xscrollbar.grid(row=1, column=0, sticky=tkinter.E+tkinter.W)

        root_yscrollbar = AutoScrollbar(master)
        root_yscrollbar.grid(row=0, column=1, sticky=tkinter.N+tkinter.S)

        _canvas = tkinter.Canvas(master, bd=0,
                                 width=canvas_width, height=canvas_height,
                                 scrollregion=(0, 0, frame_width, frame_height),
                                 xscrollcommand=root_xscrollbar.set,
                                 yscrollcommand=root_yscrollbar.set)

        _canvas.grid(row=0, column=0,
                     sticky=tkinter.N+tkinter.S+tkinter.E+tkinter.W)

        root_xscrollbar.config(command=_canvas.xview)
        root_yscrollbar.config(command=_canvas.yview)

        self.scrolled_frame = tkinter.Frame(_canvas)
        #self.scrolled_frame = tkinter.Frame(_canvas, background="blue")

        window_id = _canvas.create_window(0, 0,
                                width=frame_width, height=frame_height,
                                window=self.scrolled_frame,
                                anchor=tkinter.N+tkinter.W)

