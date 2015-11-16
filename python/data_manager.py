from collections import defaultdict
from math import floor
from forensic_path import size_string
from copy import copy
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class DataManager():
    """Contains calculated data and methods for calculating that data.
    """

    # change type signaled: data_changed, filter_changed
    change_type = ""

    # project attributes
    be_dir = ""
    image_size = 0
    image_filename = ""
    hashdb_dir = ""
    sector_size = 0
    block_size = 0
    forensic_paths = dict()
    hashes = dict()
    source_details = dict()
 
    len_forensic_paths = 0
    len_hashes = 0
    len_source_details = 0

    # source IDs
    source_ids = list()

    # annotation
    annotatioin_types = list()
    annotations = list()
    annotation_load_status = ""

    # filters
    ignore_max_hashes = 0
    ignore_flagged_blocks = True
    ignored_sources = set()
    ignored_hashes = set()
    highlighted_sources = set()
    highlighted_hashes = set()

    def __init__(self):
        self._data_manager_changed = tkinter.BooleanVar()

    def set_data(self, data_reader):
        # copy project attributes from data reader
        self.be_dir = data_reader.be_dir
        self.image_size = data_reader.image_size
        self.image_filename = data_reader.image_filename
        self.hashdb_dir = data_reader.hashdb_dir
        self.sector_size = data_reader.sector_size
        self.block_size = data_reader.block_size
        self.forensic_paths = data_reader.forensic_paths
        self.hashes = data_reader.hashes
        self.source_details = data_reader.source_details
        self.len_forensic_paths = len(data_reader.forensic_paths)
        self.len_hashes = len(data_reader.hashes)
        self.len_source_details = len(data_reader.source_details)

        # clear any filter settings
        self.ignore_max_hashes = 0
        self.ignore_flagged_blocks = True
        self.ignored_sources.clear()
        self.ignored_hashes.clear()
        self.highlighted_sources.clear()
        self.highlighted_hashes.clear()

        # set source IDs
        self.source_ids = data_reader.source_details.keys()

        # annotations
        self.annotation_types = data_reader.annotation_types
        self.annotations = data_reader.annotations
        self.annotation_load_status = data_reader.annotation_load_status

        self._fire_change("data_changed")

    def set_callback(self, f):
        """Register function f to be called on histogram mouse change."""
        self._data_manager_changed.trace_variable('w', f)

    def _fire_change(self, change_type):
        self.change_type = change_type
        self._data_manager_changed.set(True)

    # ############################################################
    # project data
    # ############################################################
    def calculate_hash_counts(self):
        """Calculate hash counts based on identified data and filter
          settings.  Data in this hash counts map is used to calculate
          bucket data plotted in the frequency histogram.

        Returns:
          hash_counts(map<hash, (count, is_ignored, is_highlighted)>):
            Data in this hash counts map is used to calculate bucket
            data plotted in the frequency histogram.
        """

        # optimization: make local references to filter variables
        ignore_max_hashes = self.ignore_max_hashes
        ignore_flagged_blocks = self.ignore_flagged_blocks
        ignored_sources = self.ignored_sources
        ignored_hashes = self.ignored_hashes
        highlighted_sources = self.highlighted_sources
        highlighted_hashes = self.highlighted_hashes

        hash_counts = dict()

        # calculate hash_counts based on identified data
        for block_hash, (count, source_id_set, _, has_label) in \
                                             self.hashes.items():
            is_ignored = False
            is_highlighted = False

            # count exceeds ignore_max_hashes
            if ignore_max_hashes != 0 and count > ignore_max_hashes:
                is_ignored = True

            # hash is ignored
            if block_hash in ignored_hashes:
                is_ignored = True

            # hash is highlighted
            if block_hash in highlighted_hashes:
                is_highlighted = True

            # flagged blocks are ignored
            if ignore_flagged_blocks and has_label:
                is_ignored = True

            # a source associated with this hash is ignored
            if len(ignored_sources.intersection(source_id_set)):
                is_ignored = True

            # a source associated with this hash is highlighted
            if len(highlighted_sources.intersection(source_id_set)):
                is_highlighted = True

            # set the count tuple for the hash
            hash_counts[block_hash] = (count, is_ignored, is_highlighted)

        return hash_counts

    def calculate_bucket_data(self, hash_counts, start_offset,
                                              bytes_per_bucket, num_buckets):
        """Buckets show number of sources that map to them.
          Call _calculate_hash_counts first to define hash_counts.

        Returns:
          source_buckets(List): List of num_buckets sorce count values.
          ignored_source_buckets(List): List of num_buckets sorce count
            values.
          highlighted_source_buckets(List): List of num_buckets sorce
            count values.
          y_scale(int): Scale to fit the list of buckets vertically.
        """
        # initialize empty buckets for each data type tracked
        source_buckets = [0] * num_buckets
        ignored_source_buckets = [0] * num_buckets
        highlighted_source_buckets = [0] * num_buckets
        y_scale = 0

        if bytes_per_bucket == 0:
            # no data
            return (source_buckets, ignored_source_buckets,
                                        highlighted_source_buckets, y_scale)


        # calculate the histogram
        for offset, block_hash in self.forensic_paths.items():
            bucket = int((offset - start_offset) // bytes_per_bucket)

            if bucket < 0 or bucket >= num_buckets:
                # offset is out of range of buckets
                continue

            # set values for buckets
            count, is_ignored, is_highlighted = hash_counts[block_hash]

            # hash and source buckets
            source_buckets[bucket] += count

            # ignored hash and source buckets
            if is_ignored:
                ignored_source_buckets[bucket] += count

            # highlighted hash and source buckets
            if is_highlighted:
                highlighted_source_buckets[bucket] += count

        # set Y scale
        # find bar with biggest count
        highest_count = max(source_buckets)
        if highest_count < 100:
            y_scale = 1
        elif highest_count < 500:
            y_scale = 5
        elif highest_count < 1000:
            y_scale = 10
        elif highest_count < 5000:
            y_scale = 50
        elif highest_count < 10000:
            y_scale = 100
        elif highest_count < 50000:
            y_scale = 500
        elif highest_count < 100000:
            y_scale = 1000
        elif highest_count < 500000:
            y_scale = 5000
        elif highest_count < 1000000:
            y_scale = 10000
        elif highest_count < 5000000:
            y_scale = 50000
        else:
            y_scale = 100000

        return (source_buckets, ignored_source_buckets,
                highlighted_source_buckets, y_scale)

    # ############################################################
    # filter actions
    # ############################################################
    def fire_filter_change(self):
        """Use this when directly changing filter state."""

    def calculate_sources_and_hashes_in_range(self, start_byte, stop_byte):
        """ Calculate sources and hashes in range.
        Returns:
          source_ids_in_range(set): Set of source IDs in range.
          hashes_in_range(set): Set of hashes in range.
        """
        # clear source IDs and hashes in any previous range
        source_ids_in_range = set()
        hashes_in_range = set()

        # done if no range
        if start_byte == stop_byte or start_byte == stop_byte + 1:
            return(source_ids_in_range, hashes_in_range)

        # iterate through forensic paths and gather data about the range
        for forensic_path, block_hash in \
                                     self.forensic_paths.items():
            offset = int(forensic_path)

            # skip if not in range
            if offset < start_byte or offset >= stop_byte:
                continue

            # get source ids in range
            # get source IDs associated with this hash
            (_, source_id_set, _, _) = self.hashes[block_hash]

            # append source IDs from this hash
            if not source_id_set.issubset(source_ids_in_range):
                source_ids_in_range = source_ids_in_range.union(source_id_set)

            # get hashes in range
            hashes_in_range.add(block_hash)

        return(source_ids_in_range, hashes_in_range)

    # ignore hashes in range
    def ignore_hashes_in_range(self, start_byte, stop_byte):
        # get shources and hashes in range
        sources, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)

        # set filters based on hashes
        self.ignored_hashes = self.ignored_hashes.union(hashes)
        self.highlighted_hashes = self.highlighted_hashes.difference(hashes)

        # fire filter change
        self._fire_change("filter_changed")

    # ignore sources with hashes in range
    def ignore_sources_with_hashes_in_range(self, start_byte, stop_byte):
        sources, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_sources = self.ignored_sources.union(sources)
        self.highlighted_sources = self.highlighted_sources.difference(sources)

        # fire filter change
        self._fire_change("filter_changed")

    # clear ignored hashes
    def clear_ignored_hashes(self):
        # clear ignored hashes and signal change
        self.ignored_hashes.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # clear ignored sources
    def clear_ignored_sources(self):
        # clear ignored sources and signal change
        self.ignored_sources.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # highlight hashes in range
    def highlight_hashes_in_range(self, start_byte, stop_byte):
        sources, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_hashes = self.ignored_hashes.difference(hashes)
        self.highlighted_hashes = self.highlighted_hashes.union(hashes)

        # fire filter change
        self._fire_change("filter_changed")

    # highlight sources with hashes in range
    def highlight_sources_with_hashes_in_range(self, start_byte, stop_byte):
        sources, hashes = self.calculate_sources_and_hashes_in_range(
                                                      start_byte, stop_byte)
        self.ignored_sources = self.ignored_sources.difference(sources)
        self.highlighted_sources = self.highlighted_sources.union(sources)

        # fire filter change
        self._fire_change("filter_changed")

    # clear highlighted hashes
    def clear_highlighted_hashes(self):
        # clear highlighted hashes and signal change
        self.highlighted_hashes.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # clear highlighted sources
    def clear_highlighted_sources(self):
        # clear highlighted sources and signal change
        self.highlighted_sources.clear()

        # fire filter change
        self._fire_change("filter_changed")

    # ############################################################
    # sources list
    # ############################################################
    def calculate_sources_list(self):
        """Calculate the sources list tuple.

        Returns:
          sources_list(list<(source_id, percent_found, text)>): List of
            tuple of sources found.
        """
        # similar to calculate_hash_counts()
        ignore_max_hashes = self.ignore_max_hashes
        ignore_flagged_blocks = self.ignore_flagged_blocks
        ignored_sources = self.ignored_sources
        ignored_hashes = self.ignored_hashes
        highlighted_sources = self.highlighted_sources
        highlighted_hashes = self.highlighted_hashes

        # data to calculate
        sources_offsets = defaultdict(set)
        highlighted_sources_offsets = defaultdict(set)

        # calculate the data
        for block_hash, (count, source_id_set, id_offset_pairs, has_label) in \
                                             self.hashes.items():

            # skip ignored hashes

            # hash count exceeds ignore_max_hashes
            if ignore_max_hashes != 0 and count > ignore_max_hashes:
                continue

            # hash has entropy label flag
            if ignore_flagged_blocks and has_label:
                continue

            # hash is in filter ignored set
            if block_hash in ignored_hashes:
                continue

            # track sources
            for source_id, file_offset in id_offset_pairs:

                # track sources not in ignored sources
                if source_id not in ignored_sources:
                    sources_offsets[source_id].add(file_offset)

                # track highlighted sources
                if block_hash in highlighted_hashes or \
                                         source_id in highlighted_sources:
                    highlighted_sources_offsets[source_id].add(file_offset)


            source_ids = self.source_details.keys()

        # now calculte the tuple of source table information

        # create a list of source information to make the sorted list from
        sources_list = list()
        temp_block_size = self.block_size
        for source_id in self.source_details.keys():
            source = self.source_details[source_id]

            # compose the source text
            # handle missing fields, which can happen if an image was
            # imported, instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                               (int((source["filesize"] + temp_block_size -1)
                               / temp_block_size)) * 100
#                print ("len source: ", len(sources_offsets[source_id]), source["filesize"], int(source["filesize"]), temp_block_size)

                text = '\t%.1f%%\t%d\t%d\t%s\t%s\t%s\n' \
                                %(percent_found,
                                  len(sources_offsets[source_id]),
                                  len(highlighted_sources_offsets[source_id]),
                                  size_string(source["filesize"]),
                                  source["repository_name"],
                                  source["filename"])

            else:
                percent_found = 1 # NOTE: this conditional will go away
                text = '\t?\t%d\t%d\t?\t%s\t%s\n' \
                                %(len(sources_offsets[source_id]),
                                  len(highlighted_sources_offsets[source_id]),
                                  source["repository_name"],
                                  source["filename"])

            # append source information tuple
            sources_list.append((source_id, percent_found, text))

        return sources_list
