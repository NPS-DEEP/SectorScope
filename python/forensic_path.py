"""helper functions for managing with bulk_extractor Forensic Paths.
"""
def offset_string(offset, offset_format, byte_alignment):
    """
    Args:
      offset (int): the offset to be formatted
    Returns:
      formatted offset string
    """
    if offset_format == "hex":
        return "0x%08x" % offset
    elif offset_format == "decimal":
        return "%s" % offset
    elif offset_format == "byte alignment":
        # return 0 if not initialized
        if byte_alignment == 0:
            return 0

        # program error if not byte aligned or one less than byte aligned
        if offset / byte_alignment != offset // byte_alignment and \
                   (offset+1) / byte_alignment != (offset+1) // byte_alignment:

            raise RuntimeError("program error")
        return "%d s" % (offset // byte_alignment)
    else:
        raise RuntimeError("program error")

def int_string(value):
    if value < 1000:
        return value
    if value < 1000000:
        return "%sK" % (value//1000)
    return "%sM" % (value//1000000)

# from http://stackoverflow.com/questions/1094841/
# reusable-library-to-get-human-readable-version-of-file-size
def size_string(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

#def offset_path(path, offset):
#    """
#    Args:
#      path (str): the forensic path input
#      offset (int): the offset to apply to the input path
#    Returns:
#      path + offset as string
#    """
#
#    # action depends on position of last '-' if present
#    index = path.rindex('-')
#        if index == -1:
#            # path is number so just add offset
#            return "%s" % (int(path) + offset)
#        else:
#            return "%s" % (int(path[index+1:]) + offset)

