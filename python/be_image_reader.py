# Adapted from bulk_extractor/python/be_image_reader.py.
import os
from subprocess import Popen,PIPE

class BEImageReader:
    """Provide utf-8 binary read of a disk image using bulk_extractor
    """

    def __init__(self,fname):
        """
        Opens and leaves open a bulk_extractor process for reading.
        Args:
          fname (str): the media image
        """
        if (not os.path.exists(fname)):
            print("%s does not exist" % fname)
            exit(1)
 
        self.fname = fname
        self.p = Popen(["bulk_extractor","-p",'-http',self.fname],
                       stdin=PIPE,stdout=PIPE,bufsize=0)

    def read(self,offset,amount):
        """Read amount of bytes starting at offset and return utf-8
        binary bytes.
        """
        def readline():
            r = b'';
            while True:
                r += self.p.stdout.read(1)
                if r[-1]==ord('\n'):
                    return r
            
        self.p.stdin.write("GET {} HTTP/1.1\r\nRange: bytes=0-{}\r\n\r\n".format(offset,amount-1).encode('utf-8'))
        params = {}
        while True:
            buf = readline().decode('utf-8').strip()
            if buf=='': break
            (n,v) = buf.split(": ")
            params[n] = v
        toread = int(params['Content-Length'])
        buf = b''
        while len(buf)!=toread:
            buf += self.p.stdout.read(toread)
        return buf

