import os
import xml
import json
import subprocess
from collections import defaultdict
from annotation_reader import read_annotations
from error_window import ErrorWindow
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataReader():
    """Read project data from a project directory to provide hash,
      source, and image data related to a block hash scan.

    This is a helper class to be used only by the data manager.

    The bulk_extractor output from a hashdb scan run must exist.  The
    identified_blocks_expanded.txt file will be created if it does not
    exist.

    The following resources are accessed:
      be_dir/report.xml
      be_dir/hashdb.hdb/settings.xml
      be_dir/identified_blocks_expanded.txt or be_dir/identified_blocks.txt

    If be_dir/identified_blocks_expanded.txt does not exist, it is
    created using be_dir/identified_blocks.txt and the other required
    resources.

    Attributes:
      be_dir (str): The bulk_extractor directory being read.
      image_size (int): Size in bytes of the media image.
      image_filename (str): Full path of the media image filename.
      hashdb_dir (str): Full path to the hash database directory.
      sector_size (int): Sector size used by the hashdb database, used for
        displaying media offset values in terms of sectors.
      block_size (int): Block size used by the hashdb database.
      forensic_paths (dict<forensic path int, hash hexcode str>):
        Dictionary maps forensic paths to their hash value.
      hashes (dict<hash hexcode str, tuple<source ID set, list id offset pair,
        bool has_label>>).  Dictionary maps hashes to hash information.
      source_details (dict<source ID int, dict<source metadata attributes>>):
        Dictionary where keys are source IDs and values are a dictionary
        of attributes associated with the given source as obtained from
        the identified_blocks_expanded.txt file.
      annotation_types (list<(type, description, is_active)>): List
        of annotation types available.
      annotations (list<(annotation_type, offset, length, text)>):
        List of image annotations that can be displayed.
      annotation_load_status (str): status of the annotation load or none
        if okay.
    """

    def __init__(self):
        # set initial state
        self.be_dir = ""
        self.image_size = 0
        self.image_filename = ""
        self.hashdb_dir = ""
        self.sector_size = -1
        self.block_size = -1
        self.forensic_paths = dict()
        self.hashes = dict()
        self.source_details = dict()
        self.annotation_types = list()
        self.annotations = list()
        self.annotation_load_status = ""

    def read(self, be_dir):
        """
        Reads and sets data else raises an exception and leaves data alone.
        Args:
          be_dir (str): The bulk_extractor output directory where the
            hashdb scanner scan was run.

        Raises read related exceptions.
        """
        # get attributes from bulk_extractor report.xml
        (image_size, image_filename, hashdb_dir) = self._read_be_report_file(
                                                                      be_dir)

        # get attributes from hashdb settings.xml
        (sector_size, block_size) = self._read_settings_file(hashdb_dir)

        # make identified_blocks_expanded.txt file if it does not exist
        self._maybe_make_identified_blocks_expanded_file(be_dir, hashdb_dir)

        # read identified_blocks_expanded.txt
        (forensic_paths, hashes, source_details) = \
                               self._read_identified_blocks_expanded(be_dir)

        # read image annotations
        try:
            annotation_types, annotations = read_annotations(
                                                     image_filename, be_dir)
            annotation_load_status = ""

        except Exception as e:
            annotation_load_status = e
            annotation_types = list()
            annotations = list()

        # everything worked so accept the data
        self.be_dir = be_dir
        self.image_size = image_size
        self.image_filename = image_filename
        self.hashdb_dir = hashdb_dir
        self.sector_size = sector_size
        self.block_size = block_size
        self.forensic_paths = forensic_paths
        self.hashes = hashes
        self.source_details = source_details
        self.annotation_types = annotation_types
        self.annotations = annotations
        self.annotation_load_status = annotation_load_status

    def __repr__(self):
        return("DataReader("
              "be_dir: '%s', Image size: %d, Image filename: '%s', "
              "hashdb directory: '%s', Sector size: %d, Block size: %d, "
              "Number of forensic paths: %d, Number of hashes: %d, "
              "Number of sources: %d, "
              "Number of image annotation types: %d, "
              "Number of image annotations: %d)"
              "" % (
                        self.be_dir,
                        self.image_size,
                        self.image_filename,
                        self.hashdb_dir,
                        self.sector_size,
                        self.block_size,
                        len(self.forensic_paths),
                        len(self.hashes),
                        len(self.source_details),
                        len(self.annotation_types),
                        len(self.annotations),
              ))

    def _read_be_report_file(self, be_dir):
        """Read image_size, image_filename, hashdb_dir from report.xml."""

        # path to report file
        be_report_file = os.path.join(be_dir, "report.xml")

        if not os.path.exists(be_report_file):
            raise ValueError("bulk_extractor Report file '%s'\n"
                             "does not exist." % be_report_file)

        xmldoc = xml.dom.minidom.parse(open(be_report_file, 'r'))

        # image size
        image_size = int((xmldoc.getElementsByTagName(
                                     "image_size")[0].firstChild.wholeText))

        # image filename
        image_filename = xmldoc.getElementsByTagName(
                           "image_filename")[0].firstChild.wholeText

        # hashdb_dir from command_line tag
        command_line = xmldoc.getElementsByTagName(
                           "command_line")[0].firstChild.wholeText
        i = command_line.find('hashdb_scan_path_or_socket=')
        if i == -1:
            raise ValueError("Path to hash database not found in %s." %
                                                            be_report_file)
        i += 27
        if command_line[i] == '"':
            # db is quoted
            i += 1
            i2 = command_line.find('"', i)
            if i2 == -1:
                raise ValueError("Close quote not found in report.xml "
                                 "under %s." % be_report_file)
            hashdb_dir = command_line[i:i2]
        else:
            # db is quoted so take text to next space
            i2 = command_line.find(' ', i)
            if i2 == -1:
                hashdb_dir = command_line[i:]
            else:
                hashdb_dir = command_line[i:i2]

        if not os.path.exists(hashdb_dir):
            raise ValueError("Error in file %s: Unable to resolve path "
                             "to hash database: '%s'" %
                             (be_report_file, hashdb_dir))
        return (image_size, image_filename, hashdb_dir)

    def _read_settings_file(self, hashdb_dir):
        """Read block_size from settings.xml."""

        # path to settings file
        hashdb_settings_file = os.path.join(hashdb_dir, "settings.xml")

        if not os.path.exists(hashdb_settings_file):
            raise ValueError("hashdb database '%s' is not valid." % hashdb_dir)
        xmldoc = xml.dom.minidom.parse(open(hashdb_settings_file, 'r'))

        # sector size from byte alignment
        sector_size = int((xmldoc.getElementsByTagName(
                                "byte_alignment")[0].firstChild.wholeText))

        # block size from hash_block_size
        block_size = int((xmldoc.getElementsByTagName(
                                "hash_block_size")[0].firstChild.wholeText))

        return (sector_size, block_size)

    def _maybe_make_identified_blocks_expanded_file(self, be_dir, hashdb_dir):
        """Create identified_blocks_expanded.txt if it does not exist yet.
        """

        # establish the path to the identified blocks expanded file
        expanded_file = os.path.join(be_dir, 'identified_blocks_expanded.txt')

        if not os.path.exists(expanded_file):
            # get the path to the identified_blocks file
            identified_blocks_file = os.path.join(be_dir,
                                                  "identified_blocks.txt")

            # make the hashdb command
            cmd = ["hashdb", "expand_identified_blocks", "-m", "0", hashdb_dir,
                   identified_blocks_file]

            # run hashdb to make the identified blocks expanded file
            with open(expanded_file, "w") as outfile:
                status=subprocess.call(cmd, stdout=outfile)
                if status != 0:
                    raise ValueError("Unable to create expanded file '%s'"
                                                           % expanded_file)

    def _read_identified_blocks_expanded(self, be_dir):

        """Read identified_blocks_expanded.txt into forensic_paths,
        hashes, and source_details dictionaries.
        """

        # establish the path to the identified blocks expanded file
        expanded_file = os.path.join(be_dir, 'identified_blocks_expanded.txt')

        # read each line
        forensic_paths=dict()
        hashes = dict()
        source_details=dict()
        with open(expanded_file, 'r') as f:
            i = 0
            for line in f:
                try:
                    i+=1
                    if line[0]=='#' or len(line)==0:
                        continue

                    # get line parts
                    (forensic_path, block_hash, json_data) = line.split("\t")

                    # store hash at forensic path
                    forensic_paths[int(forensic_path)] = block_hash

                    # store entropy label and source data for new hash
                    if block_hash not in hashes:
                        # get json data
                        extracted_json_data = json.loads(json_data)

                        # json sources
                        json_sources = extracted_json_data[1]["sources"]

                        # count
                        count = len(json_sources)

                        # source_ids and ID, offset pairs
                        source_ids = set()
                        id_offset_pairs = list()
                        for json_source in json_sources:
                            source_id = json_source["source_id"]

                            # add source ID to source_ids set
                            source_ids.add(source_id)

                            # add pair to pairs list
                            file_offset = json_source["file_offset"]
                            id_offset_pairs.append((source_id, file_offset))

                            # also store source details if first time seen
                            if "filename" in json_source:
                                source_details[source_id] = json_source

                        # has_label, currently obtained from source[0]
                        has_label = "label" in json_sources[0]

                        # store hash and attributes as (int, set, list, bool)
                        hashes[block_hash] = (count, source_ids,
                                                  id_offset_pairs, has_label)

                except Exception as e:
                    raise ValueError("Error reading file '%s' "
                             "line %d:'%s':%s\nPlease check that "
                             "identified_blocks_expanded.txt was made "
                             "using the hash database at '%s'." % (
                                     expanded_file, i, line, e, be_dir))

        return (forensic_paths, hashes, source_details)

