import tkinter

class Tooltip():
    """Create a pop-up menu with tooltip text and bind it to master."""

    def __init__(self, master, text1, text2=""):
        self._master = master
        self._is_in = False
        self._popup_menu = tkinter.Menu(master, tearoff=0)
        self._popup_menu.add_command(label=text1)
        if text2:
            self._popup_menu.add_command(label=text2)
        master.bind("<Enter>",self._enter_master)
        master.bind("<Leave>",self._exit_master)

    def _enter_master(self, e):
        # skip if already registered as entered
        if self._is_in:
            return

        # register for tooltip to open
        self._is_in = True
        self._id = self._master.after(800, self._show_tooltip)

    def _exit_master(self, e):
        if self._is_in:
            self._is_in = False
            if self._id == None:
                # tooltip is already shown so hide it
                self._hide_tooltip()
            else:
                # tooltip is not shown yet so stop the registered timer
                self._master.after_cancel(self._id)
                self._id = None

    def _show_tooltip(self):
        self._id = None
        x = self._master.winfo_rootx()
        y = self._master.winfo_rooty()
        self._popup_menu.post(x, y+25)

    def _hide_tooltip(self):
        self._popup_menu.unpost()

