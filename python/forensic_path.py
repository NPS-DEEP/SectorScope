"""helper functions for managing with bulk_extractor Forensic Paths.
"""
def offset_string(offset):
    """
    Args:
      offset (int): the offset to be formatted
    Returns:
      formatted offset string
    """
    if offset == -1:
        return "Not selected"
    else:
        return "0x%08x" % offset

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

