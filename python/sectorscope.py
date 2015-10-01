#!/usr/bin/env python3
# view block hashes

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
import json
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

# local import
from identified_data import IdentifiedData
from menu_view import MenuView
from filters import Filters
from filters_view import FiltersView
from offset_selection import OffsetSelection
from range_selection import RangeSelection
from range_selection_view import RangeSelectionView
from fit_range_selection import FitRangeSelection
from project_summary_view import ProjectSummaryView
from histogram_view import HistogramView
from offset_selection_view import OffsetSelectionView
from sources_view import SourcesView
from forensic_path import offset_string
from open_manager import OpenManager
from colors import background

# compose the GUI
def build_gui(root_window, identified_data, filters, offset_selection,
                        range_selection, fit_range_selection, open_manager):
    """The left frame holds the banner, histogram, and table of selected
    sources.  The right frame holds the table of all sources."""

    # set root window attributes
    START_WIDTH = 1000
    START_HEIGHT = 800
    root_window.title("SectorScope")
    root_window.minsize(width=400,height=300)
    root_window.geometry("1000x700")
    root_window.configure(bg=background)

    # banner frame on top for menu, filters, project data
    banner_frame = tkinter.Frame(root_window, bg=background)
    banner_frame.pack(side=tkinter.TOP, anchor="w", padx=4, pady=(4,0))

    # menu
    menu_view = MenuView(banner_frame, open_manager)
    menu_view.frame.pack(side=tkinter.LEFT, anchor="n")

    # filters
    filters_view = FiltersView(banner_frame, filters,
                                        offset_selection, range_selection)
    filters_view.frame.pack(side=tkinter.LEFT, anchor="n", padx=(40,60))

    # project summary
    project_summary_view = ProjectSummaryView(
                            banner_frame, identified_data)
    project_summary_view.frame.pack(side=tkinter.LEFT, anchor="n")

    # middle frame
    middle_frame = tkinter.Frame(root_window, bg=background)
    middle_frame.pack(side=tkinter.TOP, anchor="w", padx=4, pady=4)

    # left middle
    left_frame = tkinter.Frame(middle_frame, bg=background)
    left_frame.pack(side=tkinter.LEFT, anchor="n")

    # the range and offset selection frame in left frame
    range_and_offset_selection_frame = tkinter.Frame(left_frame)
    range_and_offset_selection_frame.pack(side=tkinter.TOP, anchor="w", pady=4)

    # the range selection view
    range_selection_view = RangeSelectionView(
                                        range_and_offset_selection_frame,
                                        identified_data, filters,
                                        range_selection, fit_range_selection)
    range_selection_view.frame.pack(side=tkinter.LEFT, anchor="w")

    # the offset selection view
    offset_selection_view = OffsetSelectionView(
                                range_and_offset_selection_frame,
                                identified_data, filters, offset_selection)
    offset_selection_view.frame.pack(side=tkinter.LEFT, anchor="w")

    # the histogram view in left_frame
    histogram_view = HistogramView(left_frame, identified_data, filters,
                      offset_selection, range_selection, fit_range_selection)
    histogram_view.frame.pack(side=tkinter.TOP, anchor="w")

    # root_window.source_frame holds source views in the middle right
    sources_view = SourcesView(middle_frame, identified_data, filters,
                      offset_selection, range_selection)
    sources_view.frame.pack(side=tkinter.LEFT, anchor="n", padx=(4,0))

# main
if __name__=="__main__":

    # parse be_dir from input
    parser = ArgumentParser(prog='sectorscope.py',
               description="View associations between scanned hashes "
                           "and their sources for the bulk_extractor "
                           "directory at path 'be_dir'.")
    parser.add_argument('-i', '--be_dir',
                        help= 'path to the bulk_extractor directory',
                        default='')
    args = parser.parse_args() 

    # initialize Tk
    root_window = tkinter.Tk()

    # the identified data dataset
    identified_data = IdentifiedData()

    # the filters data including the filter_changed trace variable
    filters = Filters()

    # the byte offset selection
    offset_selection = OffsetSelection()

    # the byte range selection
    range_selection = RangeSelection()

    # the fit byte range selection signal manager
    fit_range_selection = FitRangeSelection()

    # the open manager
    open_manager = OpenManager(root_window, identified_data, filters,
                               offset_selection, range_selection)

    # build the GUI
    build_gui(root_window, identified_data, filters, offset_selection,
                         range_selection, fit_range_selection, open_manager)

    # now open the be_dir
    open_manager.open_be_dir(args.be_dir)

    # keep Tk alive
    root_window.mainloop()

