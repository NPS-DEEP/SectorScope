#!/usr/bin/env python3
# view block hashes

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
import json
import tkinter

# local import
from identified_data import IdentifiedData
from menu_view import MenuView
from highlights import Highlights
from offset_selection import OffsetSelection
from range_selection import RangeSelection
from highlights_summary_view import HighlightsSummaryView
from project_summary_view import ProjectSummaryView
from histogram_view import HistogramView
from offset_selection_summary_view import OffsetSelectionSummaryView
from sources_view import SourcesView
from selected_sources_view import SelectedSourcesView
from forensic_path import offset_string
from open_manager import OpenManager

# compose the GUI
def build_gui(root_window, identified_data, highlights, offset_selection,
                                              range_selection, open_manager):
    """The left frame holds the banner, histogram, and table of selected
    sources.  The right frame holds the table of all sources."""

    # set root window attributes
    START_WIDTH = 1000
    START_HEIGHT = 800
    root_window.title("SectorScope")
    root_window.minsize(width=400,height=300)
    root_window.geometry("1000x700")

    # banner frame on top for menu, highlights, project data
    banner_frame = tkinter.Frame(root_window)
    banner_frame.pack(side=tkinter.TOP, anchor="w", padx=8, pady=8)

    # menu
    menu_view = MenuView(banner_frame, open_manager)
    menu_view.frame.pack(side=tkinter.LEFT, anchor="n")

    # highlights
    highlights_summary_view = HighlightsSummaryView(banner_frame, highlights)
    highlights_summary_view.frame.pack(side=tkinter.LEFT, anchor="n",
                                                           padx=(40,60))

    # project summary
    project_summary_view = ProjectSummaryView(
                            banner_frame, identified_data)
    project_summary_view.frame.pack(side=tkinter.LEFT, anchor="n")

    # middle frame
    middle_frame = tkinter.Frame(root_window)
    middle_frame.pack(side=tkinter.TOP, anchor="w")

    # left middle
    left_frame = tkinter.Frame(middle_frame)
    left_frame.pack(side=tkinter.LEFT)

    # the hash histogram view in left_frame in the middle
    histogram_view = HistogramView(left_frame, identified_data,
                                highlights, offset_selection, range_selection)
    histogram_view.frame.pack(side=tkinter.TOP, padx=8, pady=8, anchor="w")

    # the offset selection summary view in left_frame below
    offset_selection_summary_view = OffsetSelectionSummaryView(left_frame,
                                identified_data, highlights, offset_selection)
    offset_selection_summary_view.frame.pack(side=tkinter.TOP,
                                                padx=8, pady=8, anchor="w")

    # the selected sources table in left_frame below
    selected_sources_view = SelectedSourcesView(left_frame, identified_data,
                                                highlights, offset_selection)
    selected_sources_view.frame.pack(side=tkinter.TOP, padx=8, pady=8,
                                                              anchor="w")

    # root_window.source_frame holds source views in the middle right
    sources_view = SourcesView(middle_frame, identified_data, highlights)
    sources_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8, anchor="n")

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

    # the highlights data including the highlight_changed trace variable
    highlights = Highlights()

    # the byte offset selection
    offset_selection = OffsetSelection()

    # the byte range selection
    range_selection = RangeSelection()

    # the open manager
    open_manager = OpenManager(root_window, identified_data, highlights,
                               offset_selection, range_selection)

    # build the GUI
    build_gui(root_window, identified_data, highlights,
                             offset_selection, range_selection, open_manager)

    # now open the be_dir
    open_manager.open_be_dir(args.be_dir)

    # keep Tk alive
    root_window.mainloop()

