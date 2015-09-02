# use this to report an error.
import tkinter

class ErrorWindow():
    """Import using a GUI interface.
    """

    def __init__(self, master, title_text, text, e=""):
        """Args:
          text(str): The error text to report.
          e(str): The event caught.
        """

        # toplevel
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title(title_text)
        self._root_window.transient(master)

        tkinter.Label(self._root_window, text=text).pack(side=tkinter.TOP,
                                              anchor="w", padx=8, pady=8)
        tkinter.Label(self._root_window, text=e).pack(side=tkinter.TOP,
                                              anchor="w", padx=8, pady=8)
        tkinter.Button(self._root_window, text="OK",
                       command=self._handle_ok).pack( \
                            side=tkinter.TOP, padx=8, pady=8)

    def _handle_ok(self):
        self._root_window.destroy()

