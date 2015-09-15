import os
import xml
import json
import subprocess
import tkinter
from collections import defaultdict

class IdentifiedData():
    """Provides hash, source, and image data related to a block hash scan.

    Registered callbacks are called after data is changed.

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
      block_size (int): Block size used by the hashdb database.
      sector_size (int): Sector size used by the hashdb database,
        hardcoded to 512 since it is not available in identified_blocks.txt
        and 512 is currently always the expected value.
      forensic_paths (dict<forensic path str, hash hexcode str>):
        Dictionary maps forensic paths to their hash value.
      hashes (dict<hash hexcode str, sources list, see JSON>):
        Dictionary maps hashes to sources.
      source_details (dict<source ID int, dict<source metadata attributes>>):
        Dictionary where keys are source IDs and values are a dictionary
        of attributes associated with the given source as obtained from
        the identified_blocks_expanded.txt file.
      sources_offsets (dict<source ID int, set<source offset int>>)
    """

    def __init__(self):
        # instantiate the signal variable
        # Note that Tk must already be initialized for tkinter.Variable to work.
        # Note that the boolean variable is not actually used.
        self._identified_data_changed = tkinter.BooleanVar()

        # set initial state
        self.clear()

    def clear(self):
        self.be_dir = ""
        self.image_size = 0
        self.image_filename = ""
        self.hashdb_dir = ""
        self.sector_size = 512
        self.block_size = 512
        self.forensic_paths = dict()
        self.hashes = dict()
        self.source_details = dict()
        self.sources_offsets = defaultdict(set)

        # fire data changed event
        self._identified_data_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on data change."""
        self._identified_data_changed.trace_variable('w', f)

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

        # identify source offsets of every source of every matching hash
        sources_offsets = self._identify_sources_offsets()

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
        self.sources_offsets = sources_offsets

        # fire data changed event
        self._identified_data_changed.set(True)

    def _read_be_report_file(self, be_dir):
        """Read image_size, image_filename, hashdb_dir from report.xml."""

        # path to report file
        be_report_file = os.path.join(be_dir, "report.xml")

        if not os.path.exists(be_report_file):
            raise ValueError("bulk_extractor Report file '%s'\ndoes not exist.")

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
        """Read sector_size, block_size from settings.xml."""

        # path to settings file
        hashdb_settings_file = os.path.join(hashdb_dir, "settings.xml")

        if not os.path.exists(hashdb_settings_file):
            raise ValueError("hashdb database '%s' is not valid." % hashdb_dir)
        xmldoc = xml.dom.minidom.parse(open(hashdb_settings_file, 'r'))

        # sector size from byte_alignment
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
            cmd = ["hashdb", "expand_identified_blocks", self.hashdb_dir,
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
                    forensic_paths[forensic_path] = block_hash

                    # store sources for hash the first time a hash is seen
                    if block_hash not in hashes:
                        extracted_json_data = json.loads(json_data)
                        extracted_sources = extracted_json_data[1]["sources"]
                        hashes[block_hash] = extracted_sources

                        # store source details the first time a source is seen
                        # Note: source details are provided the first time a
                        #       source is shown, so process every source
                        #       to be sure to catch complete source
                        #       information when provided.
                        for hash_source in extracted_sources:
                            if "filename" in hash_source:
                                source_details[hash_source[ \
                                                   "source_id"]]=hash_source

                except ValueError:
                    raise ValueError("Error reading file '%s'\n"
                                     "line %n:'%s'\n%s" % (
                                     expanded_file, i, e))

        return (forensic_paths, hashes, source_details)

    def _identify_sources_offsets(self):
        """Get the set of offsets for each source.  The length of a set
        indicates source fullness for that source."""
        # sources_offsets = dict<source ID, set<source offset int>>
        sources_offsets = defaultdict(set)

        # identify source offsets of every source of every matching hash
        for _, sources in self.hashes.items():
            for source in sources:

                # set the offset for the source
                sources_offsets[source["source_id"]].add(source["file_offset"])

        return sources_offsets


