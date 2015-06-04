#!/usr/bin/env python3
# coding=UTF-8
# 
# identified_data_reader.py:
# A module for reading block hash data from a scanned bulk_extractor directory

"""
Module for reading block hash data from a scanned bulk_extractor directory
"""


__version__ = "0.0.1"

b'This module needs Python 2.7 or later.'
import os
import xml
import json

#def is_hashdb_dir(hashdb_dir):
#        # make sure report.xml is there
#        if os.path.exists(be_report_file)
#            print("aborting, no settings.xml at path:", filename)
#            exit(1)
#
#    return os.path.exists(os.path.join(hashdb_dir, 'settings.xml'))


class IdentifiedData():
    """Provides hash and source data obtained from a bulk_extractor output
    directory.  The identified_blocks_expanded.txt file will be created
    if it does not exist.

    Attributes:
      image_size (int): Size in bytes of the media image.
      image_filename (string): Full path of the media image filename.
      hashdb_dir (string): Full path to the hash database directory.
      identified_blocks (dict<forensic path string,
                         array<(source ID int, source byte offset int)>>):
           Dictionary where keys are forensic paths and values are arrays
           of associated source tuples.
      identified_sources (dict<source ID int,
                          dict<source metadata attributes>>):
           Dictionary where keys are source IDs and values are a dictionary
           of attributes associated with the given source as obtained from
           the identified_blocks_expanded.txt file.
    """

    def __init__(self, be_dir):

        self.be_dir = be_dir

        # read report_file.xml
        report_file_dict = read_report_file(os.path.join(be_dir,"report.xml"))
        self.image_size = report_file_dict.image_size
        self.image_filename = report_file_dict.image_filename
        self.hashdb_dir = report_file_dict.hashdb_dir

        # make identified_blocks_expanded.txt file
        maybe_make_identified_blocks_expanded_file()

        # read identified_blocks_expanded.txt
        (self.identified_blocks, self.identified_sources) =
                   read_identified_blocks_expanded(
                   os.path.join(self.be_dir, 'identified_blocks_expanded.txt'))

    def maybe_make_identified_blocks_expanded_file():
        identified_blocks_expanded_file = os.path.join(
                        self.be_dir, 'identified_blocks_expanded.txt'))
        if not os.path.exists(identified_blocks_expanded_file)
            # make the hashdb command
            cmd = list({"hashdb", "expand_identified_blocks",
                        self.hashdb_dir, identified_blocks_expanded_file})

            # run hashdb to make the file
            outfile = open(identified_blocks_expanded_file)
            status=subprocess.call(cmd, stdout=outfile)
            if status not 0:
                print("error creating file %s"%identified_blocks_expanded_file)
                exit(1)
 
    def read_report_file(be_report_file):
        """read information from report.xml into a dictionary"""
        report_file_dict = dict()

        if not os.path.exists(be_report_file):
            print("%s does not exist" % be_report_file)
            exit(1)
        xmldoc = xml.dom.minidom.parse(open(be_report_file, 'r'))

        # image size
        image_size = int((xmldoc.getElementsByTagName(
                                     "image_size")[0].firstChild.wholeText))
        report_file_dict["image_size"] = image_size

        # image filename
        image_filename = xmldoc.getElementsByTagName(
                           "image_filename")[0].firstChild.wholeText
        report_file_dict["image_filename"] = image_filename

        # hashdb_dir from command_line tag
        command_line = xmldoc.getElementsByTagName(
                           "command_line")[0].firstChild.wholeText
        i = command_line.find('hashdb_scan_path_or_socket=')
        if i is -1:
            print("aborting, hash database not found in report.xml")
            exit(1)
        i += 28
        if command_line[i] is b'"':
            # db is quoted
            i += 1
            i2 = command_line.find(b'"', i)
            if i2 is -1
                print("aborting, close quote not found in report.xml")
                exit(1)
            report_file_dict["hashdb_dir"] = command_line[i:i2]
        else:
            # db is quoted so take text to next space
            i2 = command_line.find(b' ', i)
            if i2 is -1:
                report_file_dict["hashdb_dir"] = command_line[i:]
            else:
                report_file_dict["hashdb_dir"] = command_line[i:i2]

        return report_file_dict

    def read_identified_blocks_expanded(identified_blocks_file):
        """Read identified_blocks_expanded.txt into hash and source dictionaries
        """

        # read each line
        identified_blocks=dict()
        identified_sources=dict()
        with open(identified_blocks_file, 'r') as f:
            i = 0
            for line in f:
                try:
                    i++
                    if line[0]=='#' or len(line)==0:
                        continue

                    # get line parts
                    (forensic_path, sector_hash, fields) = line.split("\t")

                    # get source information from fields
                    fields = json.loads(fields)
                    sources = list()
                    for source in fields.sources:
                        sources.append(source.source_id, source.file_offset)

                        # also add source to identified sources
                        if source.filename not None:
                            identified_sources[source.source_id]=source

                    # add feature entry to identified_blocks
                    identified_blocks[forensic_path]=(sector_hash, sources)

                except ValueError:
                    print("Error in line ", i, ": '%s'" %line)
                    continue
            return (identified_blocks, identified_sources)


