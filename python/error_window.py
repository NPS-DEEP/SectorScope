try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class ErrorWindow:
    def __init__(self, master, title, text):
        # make toplevel window
        self._root_window = tkinter.Toplevel(master)
        self._root_window.title(title)
        self._root_window.geometry('+400+400')

        error_text = tkinter.Text(self._root_window, width=60, height=8, bd=0)
        error_text.pack(anchor="w", padx=8, pady=8)
        error_text.insert(tkinter.END, "%s\n" %text)
        error_text.config(state=tkinter.DISABLED)
        ok_button = tkinter.Button(self._root_window, text="OK",
                       command=self._handle_ok)
        ok_button.pack(side=tkinter.TOP, padx=8, pady=(0,8))

        # make modal, ref http://tkinter.unpythonic.net/wiki/ModalWindow
        ok_button.focus_set()
        self._root_window.transient(master.winfo_toplevel())

        # wait for window to become ready, ref
        # http://www.vrsets.com/python/%27grab-failed%27-error-on-linux/#%22%3Ca
        while True:
            try:
                self._root_window.grab_set()
            except tkinter._tkinter.TclError:
                pass
            else:
                break
        master.winfo_toplevel().wait_window(self._root_window)

    def _handle_ok(self):
        self._root_window.destroy()

