from math import floor

class HistogramData():
    """Contains calculated data and methods for calculating that data.
    Attributes:
      source_buckets(List): List of num_buckets sorce count values.
      ignored_source_buckets(List): List of num_buckets sorce count values.
      highlighted_source_buckets(List): List of num_buckets sorce count values.
      _hash_counts(map<hash, (count, is_ignored, is_highlighted)>): Data
        in this hash counts map is used to calculate bucket data plotted
        in the frequency histogram.
      _num_buckets(int): Number of buckets in the histogram.
    """

    def __init__(self, num_buckets):
        self._num_buckets = num_buckets
        self._hash_counts = dict()
        self.source_buckets = [0] * num_buckets
        self.ignored_source_buckets = [0] * num_buckets
        self.highlighted_source_buckets = [0] * num_buckets

    def calculate_hash_counts(self, hashes, filters):
        """Calculate hash counts based on identified_data and filter
          settings.  Data in this hash counts map is used to calculate
          bucket data plotted in the frequency histogram.
        """

        # optimization: make local references to filter variables
        ignore_max_hashes = filters.ignore_max_hashes
        ignore_flagged_blocks = filters.ignore_flagged_blocks
        ignored_sources = filters.ignored_sources
        ignored_hashes = filters.ignored_hashes
        highlighted_sources = filters.highlighted_sources
        highlighted_hashes = filters.highlighted_hashes

        self._hash_counts.clear()

        # calculate _hash_counts based on identified data
        for block_hash, (count, source_id_set, has_label) in hashes.items():
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
            self._hash_counts[block_hash] = (count, is_ignored, is_highlighted)

    def calculate_bucket_data(self, forensic_paths, start_offset,
                                                           bytes_per_bucket):
        """Buckets show number of sources that map to them.
          Call calculate_hash_counts first to define hash_counts.
        """

        # initialize empty buckets for each data type tracked
        self.source_buckets = [0] * self._num_buckets
        self.ignored_source_buckets = [0] * self._num_buckets
        self.highlighted_source_buckets = [0] * self._num_buckets

        # calculate the histogram
        for offset, block_hash in forensic_paths.items():
            bucket = int((offset - start_offset) // bytes_per_bucket)

            if bucket < 0 or bucket >= self._num_buckets:
                # offset is out of range of buckets
                continue

            # set values for buckets
            count, is_ignored, is_highlighted = self._hash_counts[block_hash]

            # hash and source buckets
            self.source_buckets[bucket] += count

            # ignored hash and source buckets
            if is_ignored:
                self.ignored_source_buckets[bucket] += count

            # highlighted hash and source buckets
            if is_highlighted:
                self.highlighted_source_buckets[bucket] += count

