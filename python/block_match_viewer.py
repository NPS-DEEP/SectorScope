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
from identified_data_reader import IdentifiedData
from data_preferences import DataPreferences
from scrolled_canvas import ScrolledCanvas
from settings_view import SettingsView
from hash_zoom_bar import HashZoomBar
from image_hex_view import ImageHexView
from sources_view import SourcesView
from forensic_path import offset_string

# main
if __name__=="__main__":
    print()
    print()
    print()

    parser = ArgumentParser(prog='block_match_viewer.py',
               description='View associations between hashes and sources')
    parser.add_argument('-be_dir',
                        help= 'path to the bulk_extractor directory',
                        default= '/home/bdallen/Kitty/be_kitty_out')
    args = parser.parse_args() 
    be_dir = args.be_dir

    # read relevant data
    identified_data = IdentifiedData(be_dir)
    data_preferences = DataPreferences()

    # initialize Tk, get tkinter.Tk class instance, set title
    START_WIDTH = 1000
    START_HEIGHT = 800
    root_window = tkinter.Tk()
    root_window.title("Block Match Viewer")
    root_window.minsize(width=400,height=300)
    root_window.maxsize(width=START_WIDTH+25,height=START_HEIGHT+25)

    # the tkinter action trace variables
    max_hashes_trace_var = tkinter.IntVar()
    skip_flagged_blocks_trace_var = tkinter.BooleanVar()
    byte_offset_selection_trace_var = tkinter.IntVar()

    # the top-level frame inside a scroll window
    root_frame = ScrolledCanvas(root_window,
             canvas_width=START_WIDTH, canvas_height=START_HEIGHT,
             frame_width=START_WIDTH, frame_height=START_HEIGHT).scrolled_frame

    # root_frame.image_frame holds media image windows on the left
    image_frame = tkinter.Frame(root_frame)
    image_frame.pack(side=tkinter.LEFT, anchor="n")

    # the view settings and source data at the top
    settings_view = SettingsView(image_frame, identified_data,
                                 max_hashes_trace_var,
                                 skip_flagged_blocks_trace_var)
    settings_view.frame.pack(side=tkinter.TOP, padx=8, pady=8, anchor="w")

    # the hash zoom bar in the middle
    hash_zoom_bar = HashZoomBar(image_frame, identified_data, data_preferences,
                                byte_offset_selection_trace_var)
    hash_zoom_bar.frame.pack(side=tkinter.TOP, padx=8, pady=8, anchor="w")

    # the hex image view below
    image_hex_view = ImageHexView(image_frame,
                                  identified_data.image_filename,
                                  identified_data.block_size,
                                  byte_offset_selection_trace_var)
    image_hex_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8, anchor="w")

    # root_frame.source_frame holds source views on the right
    sources_view = SourcesView(root_frame, identified_data)
    sources_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8, anchor="n")

    root_window.mainloop()

