#!/usr/bin/python2.7
# #!/usr/bin/env python3
# view block hashes

from argparse import ArgumentParser
import math
import xml.dom.minidom
import os
try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

# local import
from data_manager import DataManager
from menu_view import MenuView
from annotation_filter import AnnotationFilter
from filters_view import FiltersView
from histogram_control import HistogramControl
from histogram_view import HistogramView
from preferences import Preferences
from sources_view import SourcesView
from open_manager import OpenManager
from scan_statistics_window import ScanStatisticsWindow
import colors

# compose the GUI
def build_gui(root_window, data_manager, annotation_filter,
                             histogram_control, open_manager, scan_window):
    """The left frame holds the banner, histogram, and table of selected
    sources.  The right frame holds the table of all sources."""

    # set root window attributes
    START_WIDTH = 1020
    START_HEIGHT = 800
    root_window.title("SectorScope")
    root_window.minsize(width=400,height=300)
    root_window.geometry("%sx%s" % (START_WIDTH, START_HEIGHT))
    root_window.configure(bg=colors.BACKGROUND)

    # left frame for most of view, top down
    left_frame = tkinter.Frame(root_window, bg=colors.BACKGROUND)
    left_frame.pack(side=tkinter.LEFT, anchor="n", padx=4)

    # menu and filters
    menu_and_filters_frame = tkinter.Frame(left_frame, bg=colors.BACKGROUND)
    menu_and_filters_frame.pack(side=tkinter.TOP, anchor="w")

    # menu
    menu_view = MenuView(menu_and_filters_frame, open_manager, scan_window,
                                                                preferences)
    menu_view.frame.pack(side=tkinter.LEFT, anchor="n", padx=(0,80), pady=4)

    # filters
    filters_view = FiltersView(menu_and_filters_frame, data_manager,
                                                            histogram_control)
    filters_view.frame.pack(side=tkinter.LEFT, anchor="n", padx=4, pady=4)

    # the histogram view
    histogram_view = HistogramView(left_frame, data_manager,
                            annotation_filter, preferences, histogram_control)
    histogram_view.frame.pack(side=tkinter.TOP, anchor="w")

    # the sources view
    sources_view = SourcesView(left_frame, data_manager, histogram_control)
    sources_view.frame.pack(side=tkinter.LEFT, anchor="n", padx=(4,0))

# main
if __name__=="__main__":

    # parse scan_file from input
    parser = ArgumentParser(prog='sectorscope.py',
               description="View associations between media iamges and "
                           "blacklist sources.")
    parser.add_argument('-i', '--scan_file',
                        help= 'path to a block hash match scan file',
                        default='')
    parser.add_argument('-m', '--alternate_media_image',
                        help= 'path to an alternate media image',
                        default='')
    parser.add_argument('-d', '--alternate_hash_database',
                        help= 'path to an alternate hash database',
                        default='')
    parser.add_argument('-s', '--sector_size',
                        help= 'sector size for sectors',
                        default=512)
    args = parser.parse_args()

    # initialize Tk
    root_window = tkinter.Tk()

    # the scan data dataset
    data_manager = DataManager()

    # the annotation filter
    annotation_filter = AnnotationFilter()

    # preferences
    preferences = Preferences()

    # histogram control
    histogram_control = HistogramControl()

    # the open manager
    open_manager = OpenManager(root_window, data_manager,
                           annotation_filter, histogram_control, preferences)

    # the scan window, hidden until show()
    scan_window = ScanStatisticsWindow(root_window, data_manager, preferences)

    # build the GUI
    build_gui(root_window, data_manager, annotation_filter,
                             histogram_control, open_manager, scan_window)

    # now open the scan_file
    if args.scan_file != "":
        open_manager.open_scan_file(args.scan_file, int(args.sector_size),
                  args.alternate_media_image, args.alternate_hash_database)

    # keep Tk alive
    root_window.mainloop()

