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
from scrolled_canvas import ScrolledCanvas
from settings_view import SettingsView
from image_overview_plot import ImageOverviewPlot
from image_detail_plot import ImageDetailPlot
from image_hex_view import ImageHexView
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

    # initialize Tk, get tkinter.Tk class instance, set title
    START_WIDTH = 700
    START_HEIGHT = 800
    root_window = tkinter.Tk()
    root_window.title("Block Match Viewer")
    root_window.minsize(width=400,height=300)
    root_window.maxsize(width=START_WIDTH+25,height=START_HEIGHT+25)

    # the tkinter action trace variables
    image_overview_byte_offset_selection_trace_var = tkinter.IntVar()
    image_detail_byte_offset_selection_trace_var = tkinter.IntVar()
    max_hashes_trace_var = tkinter.IntVar()
    skip_flagged_blocks_trace_var = tkinter.BooleanVar()

    # the top-level frame inside a scroll window
    root_frame = ScrolledCanvas(root_window,
             canvas_width=START_WIDTH, canvas_height=START_HEIGHT,
             frame_width=START_WIDTH, frame_height=START_HEIGHT).scrolled_frame

    # image_frame holds the density and detail plots above and hex view below
    image_frame = root_frame

    # the view settings and source data at the top
    settings_view = SettingsView(image_frame, identified_data,
                                 max_hashes_trace_var,
                                 skip_flagged_blocks_trace_var)
    settings_view.frame.pack(side=tkinter.TOP, padx=8, pady=8, anchor="w")

    # the density and detail plots in the middle
    image_plot_frame = tkinter.Frame(image_frame)
    image_plot_frame.pack(side=tkinter.TOP, anchor="w")

    image_overview_plot = ImageOverviewPlot(image_plot_frame, identified_data, 
                             image_overview_byte_offset_selection_trace_var)
    image_overview_plot.frame.pack(side=tkinter.LEFT, padx=8, pady=8)

    image_detail_plot = ImageDetailPlot(image_plot_frame, identified_data, 
                             image_overview_byte_offset_selection_trace_var,
                             image_detail_byte_offset_selection_trace_var)
    image_detail_plot.frame.pack(side=tkinter.LEFT, padx=8, pady=8)

    # the hex image view below
    image_hex_view = ImageHexView(image_frame,
                                  identified_data.image_filename,
                                  image_detail_byte_offset_selection_trace_var)
    image_hex_view.frame.pack(side=tkinter.LEFT, padx=8, pady=8)

#    # the hex image view below
#    image_hex_view_frame = tkinter.Frame(image_frame)
#    image_hex_view = ImageHexView(image_hex_view_frame,
#                                  identified_data.image_filename,
#                                  image_detail_byte_offset_selection_trace_var)
#    image_hex_view_frame.pack(side=tkinter.TOP, anchor="w")

    root_window.mainloop()

