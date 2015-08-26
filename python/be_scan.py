#!/usr/bin/env python3
# Use this to scan for hashes in a media image.
# Relative paths will be replaced with absolute paths.

from argparse import ArgumentParser
import subprocess
import os
import sys
import be_scan_gui

def scan_without_gui(args):
    # get absolute paths
    hashdb_dir = os.path.abspath(args.hashdb_dir)
    be_dir = os.path.abspath(args.be_dir)
    image = os.path.abspath(args.image)

    # run bulk_extractor scan
    cmd = ["bulk_extractor", "-E", "hashdb",
           "-S", "hashdb_mode=scan",
           "-S", "hashdb_block_size=%s" % args.block_size,
           "-S", "hashdb_scan_sector_size=%s" % args.sector_size,
           "-S", "hashdb_scan_path_or_socket=%s" % hashdb_dir,
           "-o", be_dir, image]

    print("Command:", cmd)

    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1) as p:
            for line in p.stdout:
                print("bulk_extractor:", line.decode(sys.stdout.encoding),
                                                                      end='')

    except FileNotFoundError:
        print("Error: bulk_extractor not found.  Please check that bulk_extractor is installed.")
        exit(1)

    if p.returncode == 0:
        print("Done.")
    else:
        print("Error runnining bulk_extractor")
        exit(1)

if __name__=="__main__":

    parser = ArgumentParser(prog='be_scan.py', description="Scan media image 'image' for block hashes matching hashes in the hashdb database at 'hashdb_dir' and put the output in new bulk_extractor directory 'be_dir'.")
    parser.add_argument('-i', '--image',
                        help= 'path to the media image', default='')
    parser.add_argument('-d', '--hashdb_dir',
                        help= 'path to the hashdb directory', default='')
    parser.add_argument('-o', '--be_dir', help= 'path to the new bulk_extractor directory to be created')
    parser.add_argument('-p', '--block_size', type=str, default='512',
            help= 'partition size of blocks to hash, default=512')
    parser.add_argument('-a', '--sector_size', type=str, default='512',
            help= 'aligned sector boundary to scan along, default=512')
    parser.add_argument('-z', '--without_gui', action="store_true",
            help= "Use command window instead of GUI")
    args = parser.parse_args()

    if args.without_gui:
        # some args are required when run without GUI
        if not args.image or not args.hashdb_dir or not args.be_dir:
            print("image, hashdb_dir and be_dir paths are required when run " \
                  "without GUI")
            exit(1)
        scan_without_gui(args)
    else:
        be_scan_gui.BEScanGUI(args)
 
