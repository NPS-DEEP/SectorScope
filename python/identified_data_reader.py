#!/usr/bin/env python3

import os
import xml
import json
import subprocess

class IdentifiedData():
    """Provides hash, source, and image data related to a block hash scan.

    The bulk_extractor output from a hashdb scan run must exist.  The
    identified_blocks_expanded.txt file will be created if it does not
    exist.

    Attributes:
      image_size (int): Size in bytes of the media image.
      image_filename (str): Full path of the media image filename.
      hashdb_dir (str): Full path to the hash database directory.
      block_size (int): Block size used by the hashdb database.
      forensic_paths (dict<forensic path str,
                      array<(source ID int, source byte offset int)>>):
        Dictionary where keys are forensic paths and values are arrays
        of associated source tuples.
      sources (dict<source ID int, dict<source metadata attributes>>):
        Dictionary where keys are source IDs and values are a dictionary
        of attributes associated with the given source as obtained from
        the identified_blocks_expanded.txt file.

      _identified_blocks_expanded_file (str): full path to file.
    """

    def __init__(self, be_dir):
        """
        Args:
          be_dir (str): The bulk_extractor output directory where the
            hashdb scanner scan was run.

        The following resources are accessed:
          be_dir/report.xml
          be_dir/hashdb.hdb/settings.xml
          be_dir/identified_blocks_expanded.txt or be_dir/identified_blocks.txt

        If be_dir/identified_blocks_expanded.txt does not exist, it is
        created using be_dir/identified_blocks.txt and the other required
        resources.
        """

        self.be_dir = be_dir

        # get attributes from bulk_extractor report.xml
        be_report_dict = self._read_be_report_file(
                                            os.path.join(be_dir,"report.xml"))
        self.image_size = be_report_dict["image_size"]
        self.image_filename = be_report_dict["image_filename"]
        self.hashdb_dir = be_report_dict["hashdb_dir"]

        # get attributes from hashdb settings.xml
        hashdb_settings_dict = self._read_settings_file(
                                os.path.join(self.hashdb_dir,"settings.xml"))
        self.block_size = hashdb_settings_dict["block_size"]

        # establish the path to the identified blocks expanded file
        self._identified_blocks_expanded_file = os.path.join(
                             self.be_dir, 'identified_blocks_expanded.txt')

        # make identified_blocks_expanded.txt file if it does not exist
        self._maybe_make_identified_blocks_expanded_file()

        # read identified_blocks_expanded.txt
        (self.forensic_paths, self.identified_sources) = \
                                     self.read_identified_blocks_expanded()

    def _read_be_report_file(self, be_report_file):
        """Read information from report.xml into a dictionary."""
        be_report_dict = dict()

        if not os.path.exists(be_report_file):
            print("%s does not exist" % be_report_file)
            exit(1)
        xmldoc = xml.dom.minidom.parse(open(be_report_file, 'r'))

        # image size
        image_size = int((xmldoc.getElementsByTagName(
                                     "image_size")[0].firstChild.wholeText))
        be_report_dict["image_size"] = image_size

        # image filename
        image_filename = xmldoc.getElementsByTagName(
                           "image_filename")[0].firstChild.wholeText
        be_report_dict["image_filename"] = image_filename

        # hashdb_dir from command_line tag
        command_line = xmldoc.getElementsByTagName(
                           "command_line")[0].firstChild.wholeText
        i = command_line.find('hashdb_scan_path_or_socket=')
        if i == -1:
            print("aborting, hash database not found in report.xml")
            exit(1)
        i += 27
        if command_line[i] == '"':
            # db is quoted
            i += 1
            i2 = command_line.find('"', i)
            if i2 == -1:
                print("aborting, close quote not found in report.xml")
                exit(1)
            be_report_dict["hashdb_dir"] = command_line[i:i2]
        else:
            # db is quoted so take text to next space
            i2 = command_line.find(' ', i)
            if i2 == -1:
                be_report_dict["hashdb_dir"] = command_line[i:]
            else:
                be_report_dict["hashdb_dir"] = command_line[i:i2]

        if not os.path.exists(be_report_dict["hashdb_dir"]):
            print("Unable to resolve path to hash database: '%s'" %
                                          be_report_dict["hashdb_dir"])
            exit(1)
        return be_report_dict

    def _read_settings_file(self, hashdb_settings_file):
        """Read information from settings.xml into a dictionary."""
        hashdb_settings_dict = dict()

        if not os.path.exists(hashdb_settings_file):
            print("%s does not exist" % hashdb_settings_file)
            exit(1)
        xmldoc = xml.dom.minidom.parse(open(hashdb_settings_file, 'r'))

        # image size
        block_size = int((xmldoc.getElementsByTagName(
                                "hash_block_size")[0].firstChild.wholeText))
        hashdb_settings_dict["block_size"] = block_size

        return hashdb_settings_dict

    def _maybe_make_identified_blocks_expanded_file(self):
        """Create identified_blocks_expanded.txt if it does not exist yet.
        """
        if not os.path.exists(self._identified_blocks_expanded_file):
            # get the path to the identified_blocks file
            identified_blocks_file = os.path.join(
                             self.be_dir, "identified_blocks.txt")

            # make the hashdb command
            cmd = ["hashdb", "expand_identified_blocks", self.hashdb_dir,
                   identified_blocks_file]

            # run hashdb to make the identified blocks expanded file
            with open(self._identified_blocks_expanded_file, "w") as outfile:
                status=subprocess.call(cmd, stdout=outfile)
                if status != 0:
                    print("error creating file %s"
                          % self._identified_blocks_expanded_file)
                    exit(1)

        return None
 
    def _read_identified_blocks_expanded(self):
        """Read identified_blocks_expanded.txt into hash and source
        dictionaries.
        """

        # read each line
        forensic_paths=dict()
        sources=dict()
        with open(self._identified_blocks_expanded_file, 'r') as f:
            i = 0
            for line in f:
                try:
                    i+=1
                    if line[0]=='#' or len(line)==0:
                        continue

                    # get line parts
                    (forensic_path, sector_hash, json_data) = line.split("\t")

                    # get source information from json data
                    json_data = json.loads(json_data)
                    #print("json_data:", json_data)
                    json_sources = json_data[1]["sources"]
                    #print("json_sources:", json_sources)

                    hash_sources = list()
                    for hash_source in json_data[1]["sources"]:
                        hash_sources.append((hash_source["source_id"],
                                             hash_source["file_offset"]))

                        # also add hash source to sources
                        if "filename" in hash_source:
                            sources[hash_source["source_id"]]=hash_source

                    # add feature entry to forensic_paths
                    forensic_paths[forensic_path]=(sector_hash, hash_sources)

                except ValueError:
                    print("Error in line ", i, ": '%s'" %line)
                    continue
            return (forensic_paths, sources)
 
    def read_identified_blocks_expanded(self, *,
                                        skip_flagged_blocks = False,
                                        skipped_sources = {},
                                        skipped_hashes = {},
                                        max_count = 0):

        """Read identified_blocks_expanded.txt into hash and source
        dictionaries, skipping data specified in the parameter list.
        """

        # read each line
        forensic_paths=dict()
        sources=dict()
        with open(self._identified_blocks_expanded_file, 'r') as f:
            i = 0
            for line in f:
                try:
                    i+=1
                    if line[0]=='#' or len(line)==0:
                        continue

                    # get line parts
                    (forensic_path, sector_hash, json_data) = line.split("\t")

                    # get source information from json data
                    json_data = json.loads(json_data)
                    #print("json_data:", json_data)
                    json_sources = json_data[1]["sources"]
                    #print("json_sources:", json_sources)

                    # process the hash sources associated with this feature line
                    # Note: always process every source to be sure to catch
                    #       complete source information when provided.
                    hash_sources = list()
                    for hash_source in json_data[1]["sources"]:

                        # log complete source information when provided
                        if "filename" in hash_source:
                            sources[hash_source["source_id"]]=hash_source

                        # skip specified sources
                        if hash_source["source_id"] in skipped_sources:
                            continue

                        # skip labeled sources if directed to
                        if skip_flagged_blocks and "label" in hash_source:
                            continue

                        # add this source
                        hash_sources.append((hash_source["source_id"],
                                             hash_source["file_offset"]))

                    # skip specified hashes
                    if sector_hash in skipped_hashes:
                        continue

                    # skip hashes with no attributed sources
                    if len(hash_sources) == 0:
                        continue

                    # skip hashes with too many sources if directed to
                    if max_count != 0 and len(hash_sources) > max_count:
                        continue

                    # add this feature entry to forensic_paths
                    forensic_paths[forensic_path]=(sector_hash, hash_sources)

                except ValueError:
                    print("Error in line ", i, ": '%s'" %line)
                    continue
            return (forensic_paths, sources)


