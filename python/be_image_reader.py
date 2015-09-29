# Adapted from bulk_extractor/python/be_image_reader.py.
from subprocess import PIPE
from compatible_popen import CompatiblePopen

def read(fname, offset, amount):
    """Read amount of bytes starting at offset and return bytearray.

    Raises several types of exceptions when unable to read.
    """
    with CompatiblePopen(["bulk_extractor","-p",'-http',fname],
                       stdin=PIPE,stdout=PIPE,bufsize=0) as p:

        p.stdin.write("GET {} HTTP/1.1\r\nRange: bytes=0-{}\r\n\r\n\r\n".
                               format(offset,amount-1).encode('utf-8'))
        a = bytearray(p.stdout.read())
        parts = a.split(b'\r\n', 4)
        if len(parts) != 5:
            raise ValueError("error reading image '%s'" % fname)
        if not parts[0].startswith(b'Content-Length: '):
            raise ValueError("error reading image '%s'" % fname)
        count = int(parts[0][16:])
        return parts[4][:count]

