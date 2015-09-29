# Adapted from bulk_extractor/python/be_image_reader.py.
import os
import hashlib
from subprocess import Popen,PIPE
from portable import CompatiblePopen

def read(fname, offset, amount):
    """Read amount of bytes starting at offset and return utf-8
    binary bytes.

    Raises exception when unable to read.
    """
    def readline():
        r = b'';
        while True:
            r += p.stdout.read(1)
            if r[-1]==ord('\n'):
                return r
    
    with CompatiblePopen(["bulk_extractor","-p",'-http',fname],
                   stdin=PIPE,stdout=PIPE,bufsize=0) as p:

        p.stdin.write("GET {} HTTP/1.1\r\nRange: bytes=0-{}\r\n\r\n\r\n".
                           format(offset,amount-1).encode('utf-8'))
        params = {}

        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())
        print("line", readline().decode('utf-8').strip())




        while True:
            buf = readline().decode('utf-8').strip()
            if buf=='': break
            (n,v) = buf.split(": ")
            params[n] = v
        toread = int(params['Content-Length'])
        buf = b''
        while len(buf)!=toread:
            buf += p.stdout.read(toread)

    return buf

