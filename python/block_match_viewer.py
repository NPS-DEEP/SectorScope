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





def get_full_plottable_data(data_dict):
    # image size
    PLOT_SIZE = 100*100

    # establish rescaler for going from image offset to data index
    rescaler = 1.0 * PLOT_SIZE / (identified_data.image_size *
                                  identified_data.block_size)
    
    # allocate empty data
    data=numpy.zeros(PLOT_SIZE)

    # set data points
    print("data_dict")
    print(data_dict)
    for key in data_dict:
        subscript = key * rescaler
        value = data_dict[key]
        #data[subscript] = value
        print("adding subscript %s" % subscript)
        data[subscript] = 100
    
    # convert data to 2D array
    full_plottable_data = data.reshape(int(math.sqrt(PLOT_SIZE)),-1)

    return full_plottable_data

def make_plot(plottable_data):
    # make plot
    # http://matplotlib.org/examples/pylab_examples/colorbar_tick_labelling_demo.html
    fig, ax = matplotlib.pyplot.subplots()
    print(type(plottable_data))
    print(plottable_data.shape)
    #cax = ax.imshow(plottable_data, cmap=matplotlib.cm.Greys)
    #matplotlib.pyplot.colorbar()
    #ax.colorbar()
    cax = ax.imshow(plottable_data, cmap=matplotlib.cm.Blues)
    ax.set_title('Matches in %s byte image' %identified_data.image_size)

    # show
    matplotlib.pyplot.show()


def start_gui():

    # get the GUI going
    import matplotlib.figure
    root = Tk.Tk()
    root.wm_title("Block Hash Matches")

    # main plot
    fig = matplotlib.figure.Figure(figsize(4,4))  # could use dbp=100
    ax = fig.add_subplot(111)
    matplotlib.pyplot.matshow(full_plottable_data, fignum=111, cmap=cm.gray)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.show()
    canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    #subplot1 = fig.add_subplot(121)
    #t = matplotlib.arrange(0.0,3,0.01)

    # plot the data
    # no make_plot(full_plottable_data)




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


    # get the full plottable data as a square array
    #full_plottable_data = get_full_plottable_data(data_dict)

    # start the GUI
    #start_gui()

    ## get the plottable image
    #plottable_image = matplotlib.pylab.


