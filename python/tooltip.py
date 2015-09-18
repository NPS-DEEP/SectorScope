import tkinter

class Tooltip():
    """Create a pop-up tooltip and bind it to master."""
    _id = ""
    _already_shown = False

    def __init__(self, master, tooltip_text):
        self._master = master
        self._root_window = tkinter.Toplevel(master)
        self._hide()
        self._root_window.overrideredirect(True)
        text = tkinter.Label(self._root_window, text=tooltip_text, bd=1,
                             padx=4, pady=4, justify=tkinter.LEFT,
                             relief=tkinter.GROOVE)
        text.pack()
        master.bind("<Motion>", self._handle_motion, add="+")
        master.bind("<B2-Motion>", self._handle_motion, add="+")
        master.bind("<B3-Motion>", self._handle_motion, add="+")
        master.bind("<Enter>", self._handle_motion, add="+")
        master.bind("<Leave>", self._handle_leave, add="+")

    def _handle_motion(self, e):
        # stop visibility and stop any delay to show
        self._hide()
        self._master.after_cancel(self._id)

        # start delay to show
        self._id = self._master.after(1500, self._show, e.x_root, e.y_root)

    def _handle_leave(self, e):
        # stop visibility and stop any delay to show
        self._hide()
        self._master.after_cancel(self._id)

    def _show(self, x_root, y_root):
        self._root_window.geometry("+%d+%d" % (x_root, y_root + 20))
        self._root_window.deiconify()

        # start delay to hide so tooltip does not show indefinitely
        self._id = self._master.after(2500, self._hide)

    def _hide(self):
        self._root_window.withdraw()

