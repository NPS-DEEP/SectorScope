#!/usr/bin/env python3
# Use this to scan for hashes in a media image.
# Relative paths will be replaced with absolute paths.

from argparse import ArgumentParser
import subprocess
import os

if __name__=="__main__":

    parser = ArgumentParser(prog='be_scan.py', description="Scan media image 'image' for block hashes matching hashes in the hashdb database at 'hashdb_dir' and put the output in new directory 'be_dir'.")
    parser.add_argument('image', help= 'path to the media image')
    parser.add_argument('hashdb_dir', help= 'path to the hashdb directory')
    parser.add_argument('be_dir', help= 'path to the new bulk_extractor directory to be created')
    parser.add_argument('-p', '--block_size', type=str, default='512',
            help= 'partition size of blocks to hash, default=512')
    parser.add_argument('-a', '--sector_size', type=str, default='512',
            help= 'aligned sector boundary to scan along, default=512')
    args = parser.parse_args()

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

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as p:
        for line in p.stdout:
            print("bulk_extractor:", line, end='')

    if p.returncode == 0:
        print("Done.")
    else:
        print("error runnining bulk_extractor")
        print("error in command:", cmd)
        exit(1)
 
