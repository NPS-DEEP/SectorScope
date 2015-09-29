# Use this to execute a command.  stdout and stderr are sent to queue.
import subprocess
import sys
import threading
from compatible_popen import CompatiblePopen
try:
    import queue
except ImportError:
    import Queue

class ThreadedSubprocess(threading.Thread):
    def __init__(self, cmd, queue):
        """Args:
          cmd(list): the command to execute using subprocess.Popen.
          queue(queue): the queue this producer will feed.
          subprocess_returncode(int): the return code from the subprocess
        """

        threading.Thread.__init__(self)
        self._cmd = cmd
        self._queue = queue
        self.subprocess_returncode = -1

    def run(self):
        # start by showing the command issued
        self._queue.put("Command: %s\n" % self._cmd)

        # run the command
        try:
            with CompatiblePopen(self._cmd,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  bufsize=1) as self._p:

                # start readers
                stdout_reader = ReaderThread("stdout", self._p.stdout,
                                             self._queue)
                stdout_reader.start()
                stderr_reader = ReaderThread("stderr", self._p.stderr,
                                             self._queue)
                stderr_reader.start()

                # wait for readers to finish since leaving the "with" block
                # will close the pipes that the readers need
                stdout_reader.join()
                stderr_reader.join()

        # python 3 uses FileNotFoundError, python 2.7 uses superclass IOError
        except IOError:
            self._queue.put("Error: %s not found.  Please check that %s "
                            "is installed.\n" %(self._cmd[0], self._cmd[0]))
            return

        # set return code
        self.subprocess_returncode = self._p.returncode

    # kill the subprocess and let the reader threads finish naturally
    def kill(self):
        self._p.kill()


class ReaderThread(threading.Thread):
    def __init__(self, name, pipe, queue):
        threading.Thread.__init__(self)
        self._name = name
        self._pipe = pipe
        self._queue = queue

    def run(self):
        # read pipe until pipe closes
        for line in self._pipe:
            self._queue.put("%s: %s" %(self._name,
                                       line.decode(sys.stdout.encoding)))

