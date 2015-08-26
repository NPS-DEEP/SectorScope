#!/usr/bin/env python3
# Use this to import hashes from a directory into a hash database.
# Relative paths will be replaced with absolute paths.

import subprocess
import queue

class ThreadedSubprocess(threading.Thread):
    def __init__(self, cmd, queue)
        """Args:
          cmd(list): the command to execute using subprocess.Popen.
          queue(queue): the queue this producer will feed.
          subprocess_returncode(int): the return code from the subprocess
        """

        threading.Thread.__init__(self)
        self._cmd = cmd
        self._queue = queue

    def run(self):

        # start by showing the command issued
        self._queue.put("Command: %s" % cmd)

        
        try:
            with subprocess.Popen(self._cmd,
                                  stdout=subprocess.PIPE, bufsize=1) as p:
                for line in p.stdout:
                    self._queue.put(line.decode(sys.stdout.encoding))
        except FileNotFoundError:
            self._queue.put("Error: %s not found.  Please check that %s "
                            "is installed." %(self._cmd[0], self._cmd[0])
            return

        if p.returncode == 0:
            self._queue.put("Done.")
        else:
            self._queue.put("Error runnining %s" % self._cmd[0])

        self.subprocess_returncode = p.returncode

