import os
import xml
import json
import subprocess
from collections import defaultdict
from forensic_path import size_string
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class SourcesData():
    """Calculates a sources list that the sources table can be populated with.

    Attributes:
      sources_list (list): Table of source data as tuple (source_id,
        percent_found, text)
    """

    def __init__(self):
        self.sources_list = list() # tuple(sourceID, percent, text)

    def calculate_sources_list(self, identified_data, filters):
        # similar to histogram_data.calculate_hash_counts()
        ignore_max_hashes = filters.ignore_max_hashes
        ignore_flagged_blocks = filters.ignore_flagged_blocks
        ignored_sources = filters.ignored_sources
        ignored_hashes = filters.ignored_hashes
        highlighted_sources = filters.highlighted_sources
        highlighted_hashes = filters.highlighted_hashes

        # data to calculate
        sources_offsets = defaultdict(set)
        highlighted_sources_offsets = defaultdict(set)

        # calculate the data
        for block_hash, (count, source_id_set, id_offset_pairs, has_label) in \
                                             identified_data.hashes.items():

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


            source_ids = identified_data.source_details.keys()

        # now calculte the tuple of source table information

        # create a list of source information to make the sorted list from
        self.sources_list.clear()
        block_size = identified_data.block_size
        for source_id in identified_data.source_details.keys():
            source = identified_data.source_details[source_id]

            # compose the source text
            # handle missing fields, which can happen if an image was
            # imported, instead of a directory of files
            if "filesize" in source:

                # calculate percent of this source file found
                percent_found = len(sources_offsets[source_id]) / \
                               (int((source["filesize"] + block_size -1)
                               / block_size)) * 100
#                print ("len source: ", len(sources_offsets[source_id]), source["filesize"], int(source["filesize"]), block_size)

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
            self.sources_list.append((source_id, percent_found, text))

