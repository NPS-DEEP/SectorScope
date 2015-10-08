from forensic_path import offset_string
from icon_path import icon_path
from tooltip import Tooltip
from be_scan_window import BEScanWindow
from be_import_window import BEImportWindow
import selection_tools
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

class FilterChanger():
    """Provides ignore and highlight functions for changing filtering:

      ignore_hashes_in_range(self, *args):
      ignore_sources_with_hashes_in_range(self, *args):
      clear_ignored_hashes(self, *args):
      clear_ignored_sources(self, *args):

      highlight_hashes_in_range(self, *args):
      highlight_sources_with_hashes_in_range(self, *args):
      clear_highlighted_hashes(self, *args):
      clear_highlighted_sources(self, *args):
    """

    def __init__(self, identified_data,
                 filters, range_selection):
        """Args:
          identified_data(IdentifiedData): Identified data about the scan.
          filters(Filters): Filters for hashes and sources.
          range_selection(RangeSelection): The selected range.
         """

        # local references
        self._identified_data = identified_data
        self._filters = filters
        self._range_selection = range_selection

    # ignore hashes in range
    def ignore_hashes_in_range(self, *args):
        # get hashes in range
        hashes = selection_tools.hashes_in_range(self._identified_data,
                                        self._range_selection.start_offset,
                                        self._range_selection.stop_offset)

        # add to ignored hashes
        for block_hash in hashes:
            self._filters.ignored_hashes.add(block_hash)

        # fire filter change
        self._filters.fire_change()

    # ignore sources with hashes in range
    def ignore_sources_with_hashes_in_range(self, *args):

        # get set of sources in range
        source_ids = selection_tools.sources_in_range(self._identified_data,
                                        self._range_selection.start_offset,
                                        self._range_selection.stop_offset)

        # add set to ignored sources
        ignored_sources = self._filters.ignored_sources
        for source_id in source_ids:
            ignored_sources.add(source_id)

        # fire filter change
        self._filters.fire_change()

    # clear ignored hashes
    def clear_ignored_hashes(self, *args):
        # clear ignored hashes and signal change
        self._filters.ignored_hashes.clear()
        self._filters.fire_change()

    # clear ignored sources
    def clear_ignored_sources(self, *args):
        # clear ignored sources and signal change
        self._filters.ignored_sources.clear()
        self._filters.fire_change()

    # ignore hashes in range
    def highlight_hashes_in_range(self, *args):

        # get hashes in range
        hashes = selection_tools.hashes_in_range(self._identified_data,
                                        self._range_selection.start_offset,
                                        self._range_selection.stop_offset)

        # add to highlighted hashes
        for block_hash in hashes:
            self._filters.highlighted_hashes.add(block_hash)

        # fire filter change
        self._filters.fire_change()

    # highlight sources with hashes in range
    def highlight_sources_with_hashes_in_range(self, *args):

        # get set of sources in range
        source_ids = selection_tools.sources_in_range(self._identified_data,
                                        self._range_selection.start_offset,
                                        self._range_selection.stop_offset)

        # add set to ignored sources
        highlighted_sources = self._filters.highlighted_sources
        for source_id in source_ids:
            highlighted_sources.add(source_id)

        # fire filter change
        self._filters.fire_change()

    # clear highlighted hashes
    def clear_highlighted_hashes(self, *args):
        # clear highlighted hashes and signal change
        self._filters.highlighted_hashes.clear()
        self._filters.fire_change()

    # clear highlighted sources
    def clear_highlighted_sources(self, *args):
        # clear highlighted sources and signal change
        self._filters.highlighted_sources.clear()
        self._filters.fire_change()
