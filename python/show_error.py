try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ShowError:
    def __init__(self, master, title, text):
        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title(title)
        self._root_window.transient(master)

        error_text = tkinter.Text(self._root_window, width=60, height=8, bd=0)
        error_text.pack(anchor="w", padx=8, pady=8)
        error_text.insert(tkinter.END, "%s\n" %text)
        error_text.config(state=tkinter.DISABLED)
        tkinter.Button(self._root_window, text="OK",
                       command=self._handle_ok).pack( \
                            side=tkinter.TOP, padx=8, pady=(0,8))
    def _handle_ok(self):
        self._root_window.destroy()

