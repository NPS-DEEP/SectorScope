#!/usr/bin/env python3
# view block hashes

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
import json
import numpy
import matplotlib
import tkinter as Tk

import matplotlib.pyplot
import matplotlib.cm

#import sys
import pylab
import matplotlib.pyplot

# local import
#import identified_data_reader
from identified_data_reader import IdentifiedData

def plot_identified_data(identified_data):

    # image size
    PLOT_SIZE = 100*100

    # establish rescaler for going from image offset to data index
    rescaler = PLOT_SIZE / identified_data.image_size
    print("rescaler")
    print(rescaler)

    # allocate empty data
    data=numpy.zeros(PLOT_SIZE)

    # set data points
    for key in identified_data.forensic_paths:
        subscript = int(key) * rescaler
        # count = len(identified_data.forensic_paths[key])
        data[subscript] = data[subscript]+1 if data[subscript] < 10 else data[subscript]
    
    # convert data to 2D array
    data_2d = data.reshape(int(math.sqrt(PLOT_SIZE)),-1)

    fig, ax = matplotlib.pyplot.subplots()
    print(type(data_2d))
    print(data_2d.shape)
    #cax = ax.imshow(data_2d, cmap=matplotlib.cm.Greys)
    cax = ax.imshow(data_2d, cmap=matplotlib.cm.Blues, interpolation="nearest")
    ax.set_title('Block match density in %s byte image' %identified_data.image_size)

    fig.colorbar(cax)

    # show
    matplotlib.pyplot.show()

# main
if __name__=="__main__":
    print()
    print()
    print()

    parser = ArgumentParser(prog='block_match_viewer.py', description='View associations between hashes and sources')
    parser.add_argument('-be_dir', help= 'path to the bulk_extractor directory' , default= '/home/bdallen/Kitty/be_kitty_out')
    args = parser.parse_args() 
    be_dir = args.be_dir

    # read relavent data
    identified_data = IdentifiedData(be_dir)

    # show the plot
    plot_identified_data(identified_data)

