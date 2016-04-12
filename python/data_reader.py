import os
import xml
import json
import subprocess
from collections import defaultdict
from annotation_reader import read_annotations
from error_window import ErrorWindow
from timestamp import ts0, ts
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataReader():
    """Read project data from a project directory to provide hash,
      source, and image data related to a block hash scan.

    This is a helper class to be used only by the data manager.

    The bulk_extractor output from a hashdb scan run must exist.

    The following resources are accessed:
      be_dir/report.xml
      be_dir/hashdb.hdb/settings.xml
      be_dir/identified_blocks.txt

    Attributes:
      be_dir (str): The bulk_extractor directory being read.
      image_size (int): Size in bytes of the media image.
      image_filename (str): Full path of the media image filename.
      hashdb_dir (str): Full path to the hash database directory.
      byte_alignment(int): The largest alignment value divisible by step
        size, usually step size.
      block_size (int): Block size used by the hashdb database.
      forensic_paths (dict<forensic path int, hash hexcode str>):
      hashes (dict<hash hexcode str, whole json data plus source_hashes>
        where source_hashes is set of source hexcodes associated with the hash)
      sources (dict<source hash, the json data under sources[i]>).
        the identified_blocks.txt file.
      annotation_types (list<(type, description, is_active)>): List
        of annotation types available.
      annotations (list<(annotation_type, offset, length, text)>):
        List of image annotations that can be displayed.
      annotation_load_status (str): status of the annotation load or none
        if okay.

    Note: this may be used to access source, offset pairs:
      for src, off in zip(pairs[0::2], pairs[1::2]):
    """

    def __init__(self):
        # set initial state
        self.be_dir = ""
        self.image_size = 0
        self.image_filename = ""
        self.hashdb_dir = ""
        self.byte_alignment = -1
        self.block_size = -1
        self.forensic_paths = dict()
        self.hashes = dict()
        self.sources = dict()
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
        t0 = ts0("data_reader.read start")

        # get attributes from bulk_extractor report.xml
        (image_size, image_filename, hashdb_dir) = self._read_be_report_file(
                                                                      be_dir)

        t1 = ts("data_reader.read finished report.xml", t0)

        # get attributes from hashdb settings.xml
        (byte_alignment, block_size) = self._read_settings_file(hashdb_dir)

        t2 = ts("data_reader.read finished settings.xml", t1)

        # read identified_blocks.txt
        (forensic_paths, hashes, sources) = \
                               self._read_identified_blocks(be_dir)
        t3 = ts("data_reader.read finished read identified_blocks", t2)

        # read image annotations
        try:
            annotation_types, annotations = read_annotations(
                                                     image_filename, be_dir)
            annotation_load_status = ""

        except Exception as e:
            annotation_load_status = e
            annotation_types = list()
            annotations = list()

        t4 = ts("data_reader.read finished read annotations.  Done.", t3)
        # everything worked so accept the data
        self.be_dir = be_dir
        self.image_size = image_size
        self.image_filename = image_filename
        self.hashdb_dir = hashdb_dir
        self.byte_alignment = byte_alignment
        self.block_size = block_size
        self.forensic_paths = forensic_paths
        self.hashes = hashes
        self.sources = sources
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
                        self.byte_alignment,
                        self.block_size,
                        len(self.forensic_paths),
                        len(self.hashes),
                        len(self.sources),
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
        i = command_line.find('hashdb_scan_path=')
        if i == -1:
            raise ValueError("Path to hash database not found in %s." %
                                                            be_report_file)
        i += 17
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
        """Read byte_alignment and block_size from settings.xml."""

        # path to settings file
        hashdb_settings_file = os.path.join(hashdb_dir, "settings.json")

        # read
        if not os.path.exists(hashdb_settings_file):
            raise ValueError("hashdb database '%s' is not valid." % hashdb_dir)
        with open(hashdb_settings_file, 'r') as f:
            json_settings = json.loads(f.readline())

        # parse
        byte_alignment = json_settings["byte_alignment"]
        block_size = json_settings["block_size"]

        return (byte_alignment, block_size)

    def _read_identified_blocks(self, be_dir):

        """Read identified_blocks.txt into forensic_paths, hashes,
        and sources dictionaries.  Also add source_hashes set.
        """

        # establish the path to the identified blocks file
        identified_blocks_file = os.path.join(be_dir, 'identified_blocks.txt')

        # read each line
        forensic_paths=dict()
        hashes = dict()
        sources=dict()
        with open(identified_blocks_file, 'r') as f:
            i = 0
            for line in f:
                line = line.strip()
                try:
                    i+=1
                    if len(line) == 0 or line[0]=='#':
                        continue

                    # get line parts
                    parts = line.split("\t")
                    if len(parts) == 3:
                        (forensic_path, block_hash, json_string) = parts

                        # store hash at forensic path
                        forensic_paths[int(forensic_path)] = block_hash

                        # store hash information if present
                        # file hashes.
                        if len(json_string.strip()) > 0:
                            # get json data
                            json_data = json.loads(json_string)

                            # hashes
                            hashes[block_hash] = json_data

                            # calculate source_hashes
                            source_hashes = set()
                            pairs = json_data["source_offset_pairs"]
                            for file_hash in pairs[0::2]:
                                source_hashes.add(file_hash)

                            # add additional field source_hashes
                            hashes[block_hash]["source_hashes"] = source_hashes

                            # sources
                            for source in json_data["sources"]:
                                sources[source["file_hash"]] = source

                    elif len(parts) == 2:
                        (forensic_path, block_hash) = parts

                        # store hash at forensic path
                        forensic_paths[int(forensic_path)] = block_hash

                    else:
                        raise ValueError("Invalid line format")

                except Exception as e:
                    raise ValueError("Error reading file '%s' "
                             "line %d:'%s':%s\nPlease check that "
                             "identified_blocks.txt was made "
                             "using the hash database at '%s'." % (
                                   identified_blocks_file, i, line, e, be_dir))

        return (forensic_paths, hashes, sources)

