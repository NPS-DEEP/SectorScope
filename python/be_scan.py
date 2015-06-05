#!/usr/bin/env python3
# Use this to scan for hashes in a media image.
# Relative paths will be replaced with absolute paths.

from argparse import ArgumentParser
import subprocess
import os

if __name__=="__main__":

    parser = ArgumentParser(prog='be_scan.py', description='Run bulk_extractor hashdb scanner')
    parser.add_argument('hashdb_dir', help= 'path to the hashdb directory')
    parser.add_argument('be_dir', help= 'path to the bulk_extractor directory')
    parser.add_argument('image', help= 'path to the media image')
    args = parser.parse_args()

    # get absolute paths
    hashdb_dir = os.path.abspath(args.hashdb_dir)
    be_dir = os.path.abspath(args.be_dir)
    image = os.path.abspath(args.image)

    # run bulk_extractor
    pathparam = "hashdb_scan_path_or_socket=%s" % hashdb_dir
    cmd = ["bulk_extractor", "-E", "hashdb", "-S", "hashdb_mode=scan",
           "-S", "hashdb_scan_path_or_socket=%s" % hashdb_dir,
           "-o", be_dir, image]

    status=subprocess.call(cmd)
    if status != 0:
        print("error runnining bulk_extractor")
        exit(1)
 
