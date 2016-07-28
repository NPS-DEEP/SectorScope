"""helper functions for managing with bulk_extractor Forensic Paths.
"""
def offset_string(offset, offset_format, sector_size):
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
    elif offset_format == "sector":
        # return 0 if not initialized
        if sector_size == 0:
            return "0 s"

        # program error if not sector aligned or one less than sector aligned
        if offset / sector_size != offset // sector_size and \
                   (offset+1) / sector_size != (offset+1) // sector_size:

            raise RuntimeError("program error")
        return "%d s" % (offset // sector_size)
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

