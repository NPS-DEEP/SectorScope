# Use this to execute a command.  stdout and stderr are sent to queue.
import os
import subprocess
import sys
import threading
from compatible_popen import CompatiblePopen
try:
    import queue
except ImportError:
    import Queue

class ThreadedScanImage(threading.Thread):
    def __init__(self, cmd, queue, outfilename):
        """Args:
          cmd(list): the command to execute using subprocess.Popen.
          queue(queue): the queue this producer will feed.
          outfilename(str): the file to save scan match results into.
          subprocess_returncode(int): the return code from the subprocess.
        """

        threading.Thread.__init__(self)
        self._cmd = cmd
        self._queue = queue
        self._outfilename = outfilename
        self.subprocess_returncode = -1

    def run(self):
        # start by showing the command issued
        self._queue.put("Command: %s\n" % self._cmd)

        # make sure outfilename does not exist yet
        if os.path.isfile(self._outfilename):
            self._queue.put(
                       "Error: %s already exists.  Aborting." % self._outfile)
            return
      
        # open outfile
        try:
            self._outfile = open(self._outfilename, 'w')
        except Exception as e:
            self._queue.put(
                    "Error: Unable to open %s.  Aborting." % self._outfilename)
            return

        # run the command
        try:
            with CompatiblePopen(self._cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 bufsize=1) as self._p:

                # start readers
                stdout_reader = StdoutReaderThread("stdout", self._p.stdout,
                                                   self._queue, self._outfile)
                stdout_reader.start()
                stderr_reader = StderrReaderThread("stderr", self._p.stderr,
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

class StdoutReaderThread(threading.Thread):
    def __init__(self, name, pipe, queue, outfile):
        threading.Thread.__init__(self)
        self._name = name
        self._pipe = pipe
        self._queue = queue
        self._outfile = outfile

    def run(self):
        # read pipe until pipe closes
        for line in self._pipe:
            line_string = line.decode(
                             encoding=sys.stdout.encoding, errors='replace')
            # write line to file
            self._outfile.write(line_string)

            # also write comment lines to queue
            if len(line_string) > 0 and line_string[0] == '#':
                self._queue.put("%s: %s" %(self._name, line_string))

class StderrReaderThread(threading.Thread):
    def __init__(self, name, pipe, queue):
        threading.Thread.__init__(self)
        self._name = name
        self._pipe = pipe
        self._queue = queue

    def run(self):
        # read pipe until pipe closes
        for line in self._pipe:
            self._queue.put("%s: %s" %(self._name, self._tcl_hack(line.decode(
                            encoding=sys.stderr.encoding, errors='replace'))))

