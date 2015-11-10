from sys import maxsize
from math import floor
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class HistogramDimensions():
    """Manages the dimensions of the histogram bar.

    Attributes:
      _num_buckets(int): Number of buckets in the histogram.
      _image_size(int): Size in bytes of the media image.
      _block_size(int): Size in bytes of one block.
      start_offset(int): Start offset, block aligned.
      bytes_per_bucket(int): Bytes per bucket, block aligned.
    """

    _num_buckets = -1
    _image_size = -1
    _block_size = -1

    # public data
    start_offset = 0
    bytes_per_bucket = -1

    def __init__(self, num_buckets):
        self._num_buckets = num_buckets
        self._histogram_dimensions_changed = tkinter.BooleanVar()

    def _set_dimensions(self, start_offset, bytes_per_bucket):
        self.start_offset = start_offset
        self.bytes_per_bucket = bytes_per_bucket
        self._histogram_dimensions_changed.set(True)

    def set_callback(self, f):
        """Register function f to be called on change."""
        self._histogram_dimensions_changed.trace_variable('w', f)

    def fit_image(self, image_size, block_size):
        """Establish image size and zoom fully out."""

        self._image_size = image_size
        self._block_size = block_size

        self._set_dimensions(0, self._round_up_to_block(self._image_size /
                                                          self._num_buckets))

    def fit_range(self, start_offset, stop_offset):
        """Fit view to range selection."""

        # If unable to expand range to whole bar place range nicely
        # inside bar, see zoom() for math.

        # calculate the range center offset
        range_center_offset = self._round_up_to_block(
                                         (start_offset + stop_offset) / 2)

        # calculate the bucket at the range center
        range_center_bucket = self.offset_to_bucket(range_center_offset)

        # calculate the new bytes per bucket
        new_bytes_per_bucket = self._round_up_to_block(
                       (stop_offset - start_offset) / self._num_buckets)

        # calculate the new start offset
        new_start_offset = range_center_offset - \
                                 new_bytes_per_bucket * range_center_bucket

        # set to left edge if too far left
        if start_offset < new_start_offset:
            new_start_offset = start_offset

        # set to right edge if too far right
        new_stop_offset = new_start_offset + \
                                      new_bytes_per_bucket * self._num_buckets
        if stop_offset > new_stop_offset:
            new_start_offset = new_start_offset - \
                              (new_stop_offset - stop_offset)

        # set the new values
        self._set_dimensions(new_start_offset, new_bytes_per_bucket)

    def pan(self, start_offset_anchor, num_buckets):
        """Pan number of buckets based on the start_offset_anchor."""

        # pan
        new_start_offset = start_offset_anchor + self.bytes_per_bucket * num_buckets

        if self._inside_graph(new_start_offset, self.bytes_per_bucket):
            # accept the pan
            self._set_dimensions(new_start_offset, self.bytes_per_bucket)

    # convert bucket to offset at left edge of bucket
    def bucket_to_offset(self, bucket):
        offset = self.start_offset + self.bytes_per_bucket * bucket

        return offset

    # convert offset to a bucket number
    def offset_to_bucket(self, image_offset):

        # initialization
        if self.bytes_per_bucket == 0:
            return -1

        # calculate bucket
        bucket = (image_offset - self.start_offset) // self.bytes_per_bucket

        return bucket

    def offset_is_on_graph(self, offset):
        """ the offset maps onto a bucket or to one past the last bucket."""
        # allow one bucket past last bucket
        bucket = self.offset_to_bucket(offset)
        return (bucket >= 0 and bucket <= self._num_buckets and
                bucket >= self.offset_to_bucket(0) and
                bucket <= self.offset_to_bucket(self._round_up_to_block(self._image_size - 1)) + 1)

    def offset_is_on_bucket(self, offset):
        """ the offset maps onto a bucket."""
        # offset maps to a bucket
        bucket = self.offset_to_bucket(offset)
        return (bucket >= 0 and bucket < self._num_buckets and
                bucket >= self.offset_to_bucket(0) and
                bucket <= self.offset_to_bucket(self._round_up_to_block(self._image_size - 1)))

    def valid_bucket_range(self):
        leftmost_bucket = self.offset_to_bucket(0)
        rightmost_bucket = self.offset_to_bucket(
                                 self._round_up_to_block(self._image_size -1))
        return leftmost_bucket, rightmost_bucket

    def zoom(self, cursor_offset, ratio):
        """Recalculate start offset and bytes per bucket."""

        # get the zoom origin bucket
        zoom_origin_bucket = self.offset_to_bucket(cursor_offset)

        # calculate the new bytes per bucket
        if ratio < 1:
            # round down to ensure zooming in
            new_bytes_per_bucket = self._round_down_to_block(
                                             self.bytes_per_bucket * (ratio))

        else:
            # round up to ensure zooming out
            new_bytes_per_bucket = self._round_up_to_block(
                                             self.bytes_per_bucket * (ratio))

        # do not let bytes per bucket reach zero
        if new_bytes_per_bucket == 0:
            new_bytes_per_bucket = self._block_size

        # calculate the new start offset
        new_start_offset = (self._round_down_to_block(cursor_offset -
                                   new_bytes_per_bucket * zoom_origin_bucket))

        if self._inside_graph(new_start_offset, new_bytes_per_bucket):
            # accept the zoom
            self._set_dimensions(new_start_offset, new_bytes_per_bucket)

    # round up to aligned block
    def _round_up_to_block(self, block_size):

        # fix decimal limitation and get as int
        block_size = int(floor(round(block_size, 5)))

        # align
        if block_size % self._block_size == 0:
            # already aligned
            return block_size

        else:
            # round up
            block_size += self._block_size - (block_size % self._block_size)
            return block_size

    # round down to aligned block
    def _round_down_to_block(self, size):

        # fix decimal limitation and get as int
        size = int(floor(round(size, 5)))

        # align
        if size % self._block_size == 0:
            # already aligned
            return size

        else:
            # round down
            size -= size % self._block_size
            return size

    def _inside_graph(self, start_offset, bytes_per_bucket):
        # the provided range is at least partially within the graph
        end_offset = start_offset + bytes_per_bucket * self._num_buckets
        return start_offset <= self._image_size and end_offset >= 0

