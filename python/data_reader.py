import os
import xml
import json
import subprocess
from collections import defaultdict
from annotation_reader import read_annotations
from error_window import ErrorWindow
from timestamp import ts0, ts
import helpers
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataReader():
    """Read project data from a scan match file to provide hash,
      source, and image data related to a block hash scan.

    This is a helper class to be used only by the data manager.

    The following resources are accessed:
      The match file created using the hashdb scan_image command.
      The hashdb settings.json file for zzzz

    Attributes:
      match_file (str): The .json scan match file.
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
        self.match_file = ""
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

    def read(self, match_file):
        """
        Reads and sets data else raises an exception and leaves data alone.
        Args:
          match_file (str): The scan match file.

        Raises read related exceptions.
        """
        # get match file metadata
        (hashdb_dir, image_filename, image_size) = \
                                 helpers.get_match_file_metadata(match_file)

        # get attributes from hashdb settings.json
        (byte_alignment, block_size) = \
                         helpers.get_byte_alignment_and_block_size(hashdb_dir)

        t0 = ts0("data_reader.read start")

        # read match file
        (forensic_paths, hashes, sources) = \
                               self._read_match_file(match_file)
        t1 = ts("data_reader.read finished read identified_blocks", t0)

        # read image annotations
#        try:
#            annotation_types, annotations = read_annotations(
#                                                     image_filename, be_dir)
#            annotation_load_status = ""
#
#        except Exception as e:
#            annotation_load_status = e
#            annotation_types = list()
#            annotations = list()
        annotation_load_status = "Not implemented zz"
        annotation_types = list()
        annotations = list()

        t4 = ts("data_reader.read finished read annotations.  Done.", t1)
        # everything worked so accept the data
        self.match_file = match_file
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
              "match_file: '%s', Image size: %d, Image filename: '%s', "
              "hashdb directory: '%s', Sector size: %d, Block size: %d, "
              "Number of forensic paths: %d, Number of hashes: %d, "
              "Number of sources: %d, "
              "Number of image annotation types: %d, "
              "Number of image annotations: %d)"
              "" % (
                        self.match_file,
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

    def _read_match_file(self, match_file):

        """Read match file into forensic_paths, hashes,
        and sources dictionaries.  Also add source_hashes set.
        """

        # read each line
        forensic_paths=dict()
        hashes = dict()
        sources=dict()
        with open(match_file, 'r') as f:
            i = 0
            for line in f:
                line = line.strip()
                try:
                    i+=1
                    if len(line) == 0 or line[0]=='#':
                        continue

                    # get line parts
                    parts = line.split("\t")
                    (forensic_path, block_hash, json_string) = parts

                    # store hash at forensic path
                    forensic_paths[int(forensic_path)] = block_hash

                    # store hash information if present
                    # get json data
                    json_data = json.loads(json_string)

                    if len(json_data) > 1:
                        # take data for hash
                        hashes[block_hash] = json_data

                        # calculate source_hashes
                        source_hashes = set()
                        pairs = json_data["source_offset_pairs"]
                        for file_hash in pairs[0::2]:
                            source_hashes.add(file_hash)

                        # add additional source_hashes field
                        hashes[block_hash]["source_hashes"] = source_hashes

                        # sources
                        for source in json_data["sources"]:
                            sources[source["file_hash"]] = source

                except Exception as e:
                    raise ValueError("Error reading file '%s' "
                             "line %d:'%s':%s\nPlease check that "
                             "this file was made using the hashdb "
                             "scan_image command." % (match_file, i, line, e))

        return (forensic_paths, hashes, sources)

