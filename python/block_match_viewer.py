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
from image_overview_plot import ImageOverviewPlot
from image_detail_plot import ImageDetailPlot
from image_hex_view import ImageHexView
from forensic_path import offset_string

def handle_mouse_click(e):
    print("e",e.x,e.y)

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
    START_WIDTH = 660
    START_HEIGHT = 800
    root = tkinter.Tk()
    root.title("Block Match Viewer")
    root.minsize(width=400,height=300)
    root.maxsize(width=START_WIDTH+25,height=START_HEIGHT+25)

    # the tkinter action variables
    image_overview_byte_offset_selection = tkinter.IntVar()
    image_detail_byte_offset_selection = tkinter.IntVar()
    hide_nonprobative_blocks = tkinter.BooleanVar()

    # the top-level frame inside a scroll window
    top_frame = ScrolledCanvas(root,
             canvas_width=START_WIDTH, canvas_height=START_HEIGHT,
             frame_width=START_WIDTH, frame_height=START_HEIGHT).scrolled_frame

    image_frame = top_frame

    # image_frame holds the density and detail plots above and hex view below

    # the image and database labels at the top
    label_frame = tkinter.Frame(image_frame)
    tkinter.Label(label_frame,
                  text='Image: %s' % identified_data.image_filename) \
                      .pack(side=tkinter.TOP, anchor="w")
    tkinter.Label(label_frame, text='Image size: %s ' %
                      offset_string(identified_data.image_size)) \
                      .pack(side=tkinter.TOP, anchor="w")
    tkinter.Label(label_frame,
                  text='Database: %s'%identified_data.hashdb_dir) \
                      .pack(side=tkinter.TOP, anchor="w")
    #label_frame.pack(side=tkinter.TOP, padx=8, pady=8)
    label_frame.pack(side=tkinter.TOP)

    # the density and detail plots in the middle
    image_plot_frame = tkinter.Frame(image_frame)
    image_overview_plot = ImageOverviewPlot(image_plot_frame, identified_data, 
                                    image_overview_byte_offset_selection)
    image_detail_plot = ImageDetailPlot(image_plot_frame, identified_data, 
                                    image_overview_byte_offset_selection,
                                    image_detail_byte_offset_selection)
    image_plot_frame.pack(side=tkinter.TOP)

    # the hex image view below
    image_hex_view_frame = tkinter.Frame(image_frame)
    image_hex_view = ImageHexView(image_hex_view_frame,
                                  identified_data.image_filename,
                                  image_detail_byte_offset_selection)
    image_hex_view_frame.pack()

    root.mainloop()

