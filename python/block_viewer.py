#!/usr/bin/env python3
# plot graph where features are found

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
import json
import numpy
import matplotlib
import tkinter as Tk

#import matplotlib.pyplot
#import matplotlib.cm

#import sys
#import pylab
#import matplotlib.pyplot
#import xml.etree.ElementTree as ET

block_size = 0
bulk_extractor_dir=""
image_size=0

def get_image_size():
    report_file = os.path.join(bulk_extractor_dir, "report.xml")
    if not os.path.exists(report_file):
        print("%s does not exist" % report_file)
        exit(1)
    xmldoc = xml.dom.minidom.parse(open(report_file, 'r'))
    image_size = int((xmldoc.getElementsByTagName("image_size")[0].firstChild.wholeText))
    return image_size

def get_data_dict():
    identified_blocks_file = os.path.join(bulk_extractor_dir, "identified_blocks.txt")
    if not os.path.exists(identified_blocks_file):
        print("%s does not exist" % identified_blocks_file)
        exit(1)

    # read each line
    data_dict=dict()
    with open(identified_blocks_file, 'r') as f:
        for line in f:
            try:
                if line[0]=='#' or len(line)==0:
                    continue

                # get line parts
                (disk_offset,sector_hash,meta) = line.split("\t")

                # get data index
                data_index = int(disk_offset)

                # get data value
                meta = json.loads(meta)
                count = int(meta['count'])
                data_value = 1/count

                # set data value at index
                data_dict[data_index] = data_value

            except ValueError:
                continue
        return data_dict

def get_full_plottable_data(data_dict):
    # image size
    IMAGE_SIZE = 100*100

    # establish rescaler for going from image offset to data index
    rescaler = 1.0 * IMAGE_SIZE / (image_size * block_size)
    
    # allocate empty data
    data=numpy.zeros(IMAGE_SIZE)

    # set data points
    for key in data_dict:
        subscript = key * rescaler
        value = data_dict[key]
        data[subscript] = value
    
    # convert data to 2D array
    full_plottable_data = data.reshape(int(math.sqrt(IMAGE_SIZE)),-1)

    return full_plottable_data

def make_plot(plottable_data):
    # make plot
    # http://matplotlib.org/examples/pylab_examples/colorbar_tick_labelling_demo.html
    fig, ax = matplotlib.pyplot.subplots()
    print(type(plottable_data))
    print(plottable_data.shape)
    #cax = ax.imshow(plottable_data, cmap=matplotlib.cm.Greys)
    cax = ax.imshow(plottable_data, cmap=matplotlib.cm.Blues)
    ax.set_title('Matches in %s byte image' %image_size)

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

    parser = ArgumentParser(prog='plot_rank.py', description='Plot media image grid showing matches')
    parser.add_argument('-be_dir', help= 'path to the bulk_extractor directory' , default= '/home/bdallen/demo8/temp2')
    parser.add_argument('-block_size', help= 'Block size in bytes' , default= 4096)
    args = parser.parse_args() 
    bulk_extractor_dir = args.be_dir
    block_size = args.block_size

    # get image size from report.xml
    image_size = get_image_size()

    # get hash match entries from identified_blocks.txt
    data_dict = get_data_dict()

    # get the full plottable data as a square array
    full_plottable_data = get_full_plottable_data(data_dict)

    # start the GUI
    start_gui()

    ## get the plottable image
    #plottable_image = matplotlib.pylab.


