import os
import xml
import json
import subprocess
from collections import defaultdict
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class SourcesData():
    """contains sources_offsets calculated by calculate_sources_offsets().

    Attributes:
      sources_offsets (dict<source ID int, set<source offset int>>):
        Source offsets of every source of every matching hash.
      highlighted_sources_offsets (dict<source ID int, set<source offset int>>):
        Source offsets of every source of every matching highlighted hash.
    """

    def __init__(self):
        self.sources_offsets = defaultdict(set)
        self.highlighted_sources_offsets = defaultdict(set)

    def calculate_sources_offsets(self, identified_data, filters):
        # similar to histogram_data.calculate_hash_counts()
        ignore_max_hashes = filters.ignore_max_hashes
        ignore_flagged_blocks = filters.ignore_flagged_blocks
        ignored_sources = filters.ignored_sources
        ignored_hashes = filters.ignored_hashes
        highlighted_sources = filters.highlighted_sources
        highlighted_hashes = filters.highlighted_hashes

        # data to calculate
        self.sources_offsets.clear()
        self.highlighted_sources_offsets.clear()

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
                    self.sources_offsets[source_id].add(file_offset)

                # track highlighted sources
                if block_hash in highlighted_hashes or \
                                         source_id in highlighted_sources:
                    self.highlighted_sources_offsets[source_id].add(file_offset)

