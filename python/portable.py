"""This code enables SectorScope to be backword-compatible with Python 2.7.

  For compatibility with tkFileDialog use this:
    portable.askdirectory()
    portable.askopenfilename()

  For compatibility with Popen use this:
    CompatiblePopen()
    
"""
import subprocess
try:
    # python3
    import tkinter
except ImportError:
    # python 2.7
    import Tkinter as tkinter
    import tkFileDialog

def askdirectory(**kwargs):
    try:
        # python 3.x
        return tkinter.filedialog.askdirectory(**kwargs)
    except AttributeError:
        # python 2.7
        return tkFileDialog.askdirectory(**kwargs)

def askopenfilename(**kwargs):
    try:
        # python 3.x
        return tkinter.filedialog.askopenfilename(**kwargs)
    except AttributeError:
        # python 2.7
        return tkFileDialog.askopenfilename(**kwargs)

# Taken from http://stackoverflow.com/questions/30421003/exception-handling-when-using-pythons-subprocess-popen
class CompatiblePopen(subprocess.Popen):
    """Fix Python 2.7 so Popen works with Python with-as keywords."""

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.stdout:
            self.stdout.close()
        if self.stderr:
            self.stderr.close()
        if self.stdin:
            self.stdin.close()
        # Wait for the process to terminate, to avoid zombies.
        self.wait()


