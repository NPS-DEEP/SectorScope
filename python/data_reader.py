import os
import xml
import json
import subprocess
from collections import defaultdict
from annotation_reader import read_annotations
from timestamp import ts0, ts
import helpers
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataReader():
    """Read identified blocks from a scan file to provide hash,
      source, and image data related to a block hash scan.

    This is a helper class to be used only by the data manager.

    Attributes:
      scan_file (str): The .json block hash scan file.
      image_size (int): Size in bytes of the media image.
      image_filename (str): Full path of the media image filename.
      hashdb_dir (str): Full path to the hash database directory.
      sector_size(int): The sector size to view.
      hash_block_size(int): The size of the hashed blocks.
      forensic_paths (list<forensic path int, hash hexcode str>): List
        of int forensic paths and their hash hexcode.
      hashes (dict<hash hexcode str, whole json data plus source_hashes>)
        where source_hashes is the set of source hexcodes associated with
        the hash, composed from every third source_offset.
      sources (dict<source hash, the json data under sources[i]>).
      annotation_types (list<(type, description, is_active)>): List
        of annotation types available.
      annotations (list<(annotation_type, offset, length, text)>):
        List of image annotations that can be displayed.
      annotation_load_status (str): status of the annotation load or none
        if okay.

    Note: this may be used to access source_offsets:
      for src, sub_count, off in zip(source_offsets[0::3],
                            source_offsets[1::3], source_offsets[2::3]):
    """

    def __init__(self):
        # set initial state
        self.scan_file = ""
        self.image_size = 0
        self.image_filename = ""
        self.hashdb_dir = ""
        self.sector_size = 0
        self.hash_block_size = 0
        self.forensic_paths = list()
        self.hashes = dict()
        self.sources = dict()
        self.annotation_types = list()
        self.annotations = list()
        self.annotation_load_status = ""

    def read(self, scan_file, sector_size, alternate_image_filename):
        """
        Reads and sets data else raises an exception and leaves data alone.
        Args:
          scan_file(str): The block hash scan file containing the identified
                          blocks.
          sector_size(int): The minimum resolution to zoom down to.
          alternate_image_filename(str): An alternate path to read the media
                          image from, or blank to read and use the default.
 
        Raises read related exceptions.
        """
        # read scan file attributes
        image_filename, image_size, hashdb_dir = \
                                 helpers.get_scan_file_attributes(scan_file)

        # use the alternate media image if it is defined
        if alternate_image_filename:
            image_filename = alternate_image_filename

        # read hash_block_size used for calculating block hashes
        hash_block_size = helpers.get_hash_block_size(hashdb_dir)

        t0 = ts0("data_reader.read start")

        # read scan file
        (forensic_paths, hashes, sources) = \
                               self._read_hash_scan_file(scan_file)
        t1 = ts("data_reader.read finished read identified_blocks", t0)

        # read image annotations

        try:
            annotation_types, annotations = read_annotations(
                                image_filename, "temp_image_annotations_dir")
            annotation_load_status = ""

        except Exception as e:
            annotation_load_status = e
            annotation_types = list()
            annotations = list()

        t4 = ts("data_reader.read finished read annotations.  Done.", t1)
        # everything worked so accept the data
        self.scan_file = scan_file
        self.image_size = image_size
        self.image_filename = image_filename
        self.hashdb_dir = hashdb_dir
        self.sector_size = sector_size
        self.hash_block_size = hash_block_size
        self.forensic_paths = forensic_paths
        self.hashes = hashes
        self.sources = sources
        self.annotation_types = annotation_types
        self.annotations = annotations
        self.annotation_load_status = annotation_load_status

    def __repr__(self):
        return("DataReader("
              "scan_file: '%s', Image size: %d, Image filename: '%s', "
              "hashdb directory: '%s', Sector size: %d, Block size: %d "
              "Number of forensic paths: %d, Number of hashes: %d, "
              "Number of sources: %d, "
              "Number of image annotation types: %d, "
              "Number of image annotations: %d)"
              "" % (
                        self.scan_file,
                        self.image_size,
                        self.image_filename,
                        self.hashdb_dir,
                        self.sector_size,
                        self.hash_block_size,
                        len(self.forensic_paths),
                        len(self.hashes),
                        len(self.sources),
                        len(self.annotation_types),
                        len(self.annotations),
              ))

    def _read_hash_scan_file(self, scan_file):

        """Read hash scan file into forensic_paths, hashes, and sources
        data structures.  Also add source_hashes set into hashes dictionary.
        """

        # read each line
        forensic_paths = dict()
        hashes = dict()
        sources = dict()
        with open(scan_file, 'r') as f:
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

                    if "source_offsets" in json_data:
                        # take data for hash
                        hashes[block_hash] = json_data

                        # calculate source_hashes
                        source_hashes = set()
                        source_offsets = json_data["source_offsets"]
                        for file_hash in source_offsets[0::3]:
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
                             "scan_image command." % (scan_file, i, line, e))

        return (forensic_paths, hashes, sources)

