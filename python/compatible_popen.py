"""Enable SectorScope to be backword-compatible with Python 2.7 by
providing functions required by Python's with-as keywords.
"""
import subprocess
# Taken from http://stackoverflow.com/questions/30421003/exception-handling-when-using-pythons-subprocess-popen
class CompatiblePopen(subprocess.Popen):

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


