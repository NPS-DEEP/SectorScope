#!/usr/bin/env python3
# view block hashes

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
import json
import tkinter

# local import
#import identified_data_reader
from identified_data import IdentifiedData
from filters import Filters
from scrolled_canvas import ScrolledCanvas
from control_view import ControlView
from identified_data_summary_view import IdentifiedDataSummaryView
from hash_histogram_bar import HashHistogramBar
from image_hex_view import ImageHexView
from sources_view import SourcesView
from forensic_path import offset_string
from open_manager import OpenManager

# compose the GUI
def build_gui(root_window, identified_data, filters,
                              byte_offset_selection_trace_var, open_manager):
    # set root window attributes
    START_WIDTH = 1000
    START_HEIGHT = 800
    root_window.title("SectorScope")
    root_window.minsize(width=400,height=300)
    root_window.maxsize(width=START_WIDTH+25,height=START_HEIGHT+25)

    # build the top-level frame inside a scroll window
    root_frame = ScrolledCanvas(root_window,
             canvas_width=START_WIDTH, canvas_height=START_HEIGHT,
             frame_width=START_WIDTH, frame_height=START_HEIGHT).scrolled_frame

    # root_frame.image_frame holds media image windows on the left
    image_frame = tkinter.Frame(root_frame)
    image_frame.pack(side=tkinter.LEFT, anchor="n")

    # the filter and identified data summary views in image_frame at the top
    control_and_summary_frame = tkinter.Frame(image_frame)
    control_and_summary_frame.pack(side=tkinter.TOP, anchor="w")

    # the filter view in control_and_summary_frame on left
    control_view = ControlView(control_and_summary_frame, filters, open_manager)
    control_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8)

    # the summary view in control_and_summary_frame on right
    identified_data_summary_view = IdentifiedDataSummaryView(
                                  control_and_summary_frame, identified_data)
    identified_data_summary_view.frame.pack(side=tkinter.LEFT, padx=40)

    # the hash histogram bar in image_frame in the middle
    hash_histogram_bar = HashHistogramBar(image_frame, identified_data, filters,
                                byte_offset_selection_trace_var)
    hash_histogram_bar.frame.pack(side=tkinter.TOP, padx=8, pady=8, anchor="w")

    # the hex image view in image_frame below
    image_hex_view = ImageHexView(image_frame, identified_data, filters,
                                  byte_offset_selection_trace_var)
    image_hex_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8, anchor="w")

    # root_frame.source_frame holds source views on the right
    sources_view = SourcesView(root_frame, identified_data, filters)
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

    # the filters including the filter_changed trace variable
    filters = Filters()

    # the tkinter action trace variable for byte offset selection
    byte_offset_selection_trace_var = tkinter.IntVar()
    byte_offset_selection_trace_var.set(-1)

    # the open manager
    open_manager = OpenManager(root_window, identified_data, filters,
                               byte_offset_selection_trace_var)

    # build the GUI
    build_gui(root_window, identified_data, filters,
                              byte_offset_selection_trace_var, open_manager)

    # now open the be_dir
    open_manager.open_be_dir(args.be_dir)

    # keep Tk alive
    root_window.mainloop()

