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

"""Read scan file and return image_filename, image_size, hashdb_dir
   Raises exception on error."""
def get_scan_file_attributes(scan_file):

    with open(scan_file, 'r') as f:

        # get hashdb_dir and image_filename from first line
        line = f.readline().strip()   # line without newline
        print("line '%s'"%line)
        if line[:11] == '# command: ':
            parts = line.split(' ')# may need to harden for quoted parameters
            print("parts", parts)
            hashdb_dir = parts[-2]
            image_filename = parts[-1]
            print("line-1 '%s'"%image_filename)
        else:
            raise ValueError("Invalid format in first line of scan"
                             " file %s" % scan_file)

        # skip the hashdb-Version line
        line = f.readline()
        if line[:18] != '# hashdb-Version: ':
            raise ValueError("Invalid format in second line of scan"
                             " file %s" % scan_file)

        # get image size from third line
        line = f.readline()
        if line[:11] == '# Scanning ':
            parts = line.split(' ')
            image_size = int(parts[-1])
        else:
            raise ValueError("Invalid format in second line of scan"
                             " file %s" % scan_file)

        return image_filename, image_size, hashdb_dir

"""Read bytes from an image file, return error_message, image_bytes."""
def read_image_bytes(image_filename, offset, count):
    if offset < 0:
        raise ValueError("Invalid negative offset requested.")

    cmd = ["hashdb", "read_bytes", image_filename, str(offset), str(count)]
    with CompatiblePopen(cmd, stdout=PIPE, stderr=PIPE) as p:

        stdout_data, stderr_data = p.communicate()
        stdout_bytearray = bytearray(stdout_data)
        stderr_text = stderr_data.decode('utf-8')

        if p.returncode != 0:
            error_message = "Error reading image bytes, " \
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

