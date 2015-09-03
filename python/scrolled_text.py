# Use this to import hashes from a directory into a hash database.
# Relative paths are replaced with absolute paths.

import tkinter

class ScrolledText():
    """A Text widget with scrollbars.

    Attributes:
      scroll_frame(Frame): The scrollable frame.
      text(Text): The text widget being scrolled.
    """

    def __init__(self, master, *, width=40, height=12):
        """Args:
          width, height(int): Dimension in text characers.
        """

        # scroll frame
        self.scroll_frame = tkinter.Frame(master, bd=1,
                                     relief=tkinter.SUNKEN)
        self.scroll_frame.pack()
        self.scroll_frame.grid_rowconfigure(0, weight=1)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # xscrollbar in scroll frame
        xscrollbar = tkinter.Scrollbar(self.scroll_frame, bd=0,
                                       orient=tkinter.HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=tkinter.E + tkinter.W)

        # yscrollbar in scroll frame
        yscrollbar = tkinter.Scrollbar(self.scroll_frame, bd=0)
        yscrollbar.grid(row=0, column=1, sticky=tkinter.N + tkinter.S)

        # text area in scroll frame
        self.text = tkinter.Text(self.scroll_frame, wrap=tkinter.NONE,
                                     width=width, height=height,
                                     bd=0,
                                     xscrollcommand=xscrollbar.set,
                                     yscrollcommand=yscrollbar.set)
        self.text.grid(row=0, column=0, sticky=tkinter.N +
                                 tkinter.S + tkinter.E + tkinter.W)

        xscrollbar.config(command=self.text.xview)
        yscrollbar.config(command=self.text.yview)

