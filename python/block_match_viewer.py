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
from image_overview_plot import ImageOverviewPlot

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

    # show the plot
    root = tkinter.Tk()
    root.title("Block Match Viewer")

    selected_offset = tkinter.IntVar()
    image_overview_plot = ImageOverviewPlot(root, identified_data, 
                                            selected_offset)

    ## media image canvas for the image overview and image detail plots
    #media_canvas = tkinter.Canvas(root, width=1100, height=600)
    #media_canvas.pack(fill=tkinter.BOTH)

    ## add the image overview plot to the image canvas
    #image_overview_plot = ImageOverviewPlot()
    #image_overview_plot.set(identified_data)
    #media_canvas.create_image(20, 20, image=image_overview_plot.photo_image,
    #                          anchor=tkinter.NW)

    ## zz
    ##image_overview_plot.photo_image.bind('Any-Motion', handle_mouse_click)
    #media_canvas.bind('<Any-Motion>', handle_mouse_click)

    root.mainloop()


