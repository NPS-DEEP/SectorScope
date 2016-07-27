# Use this to execute a command.  stdout and stderr are sent to queue.
import os
import subprocess
import sys
import threading
try:
    import queue
except ImportError:
    import Queue

# the private command thread run method
class _RunnerThread(threading.Thread):
    def __init__(self, cmd, queue):
        threading.Thread.__init__(self)
        self._cmd = cmd
        self._queue = queue

    def run(self):
        # start by showing the command issued
        self._queue.put(("Command", "%s\n"%(self._cmd)))

        # run the command
        try:
            self.cmd_p = subprocess.Popen(self._cmd, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

            # start readers
            stdout_reader = _ReaderThread("stdout", self.cmd_p.stdout, self._queue)
            stdout_reader.start()
            stderr_reader = _ReaderThread("stderr", self.cmd_p.stderr, self._queue)
            stderr_reader.start()

            # wait for threads to finish
            self.cmd_p.wait()
            stdout_reader.join()
            stderr_reader.join()

        # python 3 uses FileNotFoundError, python 2.7 uses superclass IOError
        except IOError:
            self._queue.put(("Error", "%s not found.  Please check that it "
                      "is installed.\n" % self._cmd[0]))
            return 1

# private reader helper
class _ReaderThread(threading.Thread):
    def __init__(self, name, pipe, queue):
        threading.Thread.__init__(self)
        self._name = name
        self._pipe = pipe
        self._queue = queue

    def run(self):
        # read pipe until pipe closes
        for line in self._pipe:
            line_string = line.decode(
                             encoding=sys.stderr.encoding, errors='replace')
            # write stderr line to queue
            self._queue.put((self._name, line_string))

# the command runner
class CommandRunner():
    """Run cmd and place labeled stderr and stdout text into queue.
       Places the error code of the command thread in return_code
       when done."""

    def __init__(self, cmd, queue):
        """Args:
          cmd(list): the command to execute using subprocess.Popen.
          queue(queue): the queue this producer will feed.
        """
        self._runner_thread = _RunnerThread(cmd, queue)
        self._runner_thread.start()

    # kill the subprocess and let the reader threads finish when consumed
    def kill(self):
        # cmd_p may not exist
        try:
            self._runner_thread.cmd_p.kill()
        except NameError:
            pass

    # threads are done and all output is enqueued
    def is_done(self):
        return not self._runner_thread.isAlive()

    # the return code from running the command
    def return_code(self):
        if not self.is_done():
            raise RuntimeError("usage error")
        try:
            return self._runner_thread.cmd_p.returncode
        except AttributeError:
            return -1

