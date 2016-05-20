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

"""Read settings.json and return byte_alignment and block_size.
   Raises exception on error."""
def get_byte_alignment_and_block_size(hashdb_dir):

    # return settings object from settings file
    settings_filename = os.path.join(hashdb_dir, "settings.json")
    with open(settings_filename, 'r') as settings_file:
        line = settings_file.readline()
        settings = json.loads(line)
        byte_alignment = settings["byte_alignment"]
        block_size = settings["block_size"]
        return byte_alignment, block_size

"""Read match file and return (hashdb_dir, media_image, image_size).
   Raises exception on error."""
def get_match_file_metadata(match_file):

    with open(match_file, 'r') as settings_file:

        # get hashdb_dir and media_image from first line
        line = settings_file.readline().strip()   # line without newline
        if line[:12] == '# Command: "':
            command = line[12:-1]     # part inside outer quotes
            parts = command.split(' ')# may need to harden for quoted parameters
            hashdb_dir = parts[-2]
            media_image = parts[-1]
        else:
            raise ValueError("Invalid format in first line of match"
                             " file %s" % match_file)

        # get image size from second line
        line = settings_file.readline()
        if line[:21] == '# Scanning from byte ':
            parts = line.split(' ')
            image_size = int(parts[-1])
        else:
            raise ValueError("Invalid format in second line of match"
                             " file %s" % match_file)

        return hashdb_dir, media_image, image_size

"""Read bytes from an image file, return error_message, image_bytes."""
def read_image_bytes(media_image_file, offset, count):

    cmd = ["hashdb", "read_bytes", media_image_file, str(offset), str(count)]
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

