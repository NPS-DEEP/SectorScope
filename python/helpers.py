#!/usr/bin/python
#
# hashdb_helpers.py
# A module for helping with hashdb tests
from subprocess import Popen, PIPE
import os
import shutil
import json
from compatible_popen import CompatiblePopen

"""Run command and return error_message and lines, "" on success."""
def run_short_command(cmd):

    # run command
    with CompatiblePopen(cmd, stdout=PIPE, stderr=PIPE) as p:

        stdoutdata, stderrdata = p.communicate()
        stdout_lines = stdoutdata.decode('utf-8').split("\n")
        stderr_text = stderrdata.decode('utf-8')

        if p.returncode != 0:
            error_message = "Error with" \
                            " command %s: %s" % (" ".join(cmd), stderr_text)
            return error_message, stdout_lines
        else:
            return "", stdout_lines

"""Read settings.json and return block_size.
   Raises exception on error."""
def get_hash_block_size(hashdb_dir):

    # return settings object from settings file
    settings_filename = os.path.join(hashdb_dir, "settings.json")
    with open(settings_filename, 'r') as settings_file:
        line = settings_file.readline()
        settings = json.loads(line)
        block_size = settings["block_size"]
        return block_size

"""Read scan file and return media_filename, media_size, hashdb_dir
   Raises exception on error."""
def get_scan_file_attributes(scan_file):

    with open(scan_file, 'r') as f:

        # get hashdb_dir and media_filename from first line
        line = f.readline().strip()   # line without newline
        if line[:11] == '# command: ':
            parts = line.split(' ')# may need to harden for quoted parameters
            hashdb_dir = parts[-2]
            media_filename = parts[-1]
        else:
            raise ValueError("Invalid format in first line of scan"
                             " file %s" % scan_file)

        # skip the hashdb-Version line
        line = f.readline()
        if line[:18] != '# hashdb-Version: ':
            raise ValueError("Invalid format in second line of scan"
                             " file %s" % scan_file)

        # get media size from third line
        line = f.readline()
        if line[:11] == '# Scanning ':
            parts = line.split(' ')
            media_size = int(parts[-1])
        else:
            raise ValueError("Invalid format in second line of scan"
                             " file %s" % scan_file)

        return media_filename, media_size, hashdb_dir

"""Read bytes from a media image file.  Returns: error_message else "",
   media_bytes
"""
def read_media_bytes(media_filename, offset, count):
    if offset < 0:
        raise ValueError("Invalid negative offset requested.")

    cmd = ["hashdb", "read_media", media_filename, str(offset), str(count)]
    with CompatiblePopen(cmd, stdout=PIPE, stderr=PIPE) as p:

        stdout_data, stderr_data = p.communicate()
        stdout_bytearray = bytearray(stdout_data)
        stderr_text = stderr_data.decode('utf-8')

        if p.returncode != 0:
            error_message = "Error reading media bytes, " \
                            "command %s: %s" % (" ".join(cmd), stderr_text)
            return error_message, stdout_bytearray
        else:
            return "", stdout_bytearray

"""Read the hashdb version."""
def read_hashdb_version():

    cmd = ["hashdb", "-v"]
    with CompatiblePopen(cmd, stdout=PIPE, stderr=PIPE) as p:

        stdout_data, stderr_data = p.communicate()
        stdout_text = stdout_data.decode('utf-8')
        stderr_text = stderr_data.decode('utf-8')

        if p.returncode == 0:
            return stdout_text
        else:
            return "hashdb is not available."

"""Convert a byte offset to a printable formatted string.
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

        # Offsets are usually sector aligned, but offsets under a recursion
        # path may not be.
        # program error if not sector aligned or one less than sector aligned
        if float(offset) / sector_size == offset // sector_size or \
            float(offset+1) / sector_size == (offset+1) // sector_size:

            # this offset is sector aligned
            return "%d s" % (offset // sector_size)

        else:
            # not sector aligned
            return "%3.1f s" % (offset / sector_size)
    else:
        raise RuntimeError("program error")

"""Scale an integer as a printable formatted string.
"""
def int_string(value):
    if value < 1000:
        return value
    if value < 1000000:
        return "%sK" % (value//1000)
    return "%sM" % (value//1000000)

"""Scale a byte offset as a printable formatted string.
"""
# from http://stackoverflow.com/questions/1094841/
# reusable-library-to-get-human-readable-version-of-file-size
def size_string(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

