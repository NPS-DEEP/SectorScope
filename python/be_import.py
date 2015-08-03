#!/usr/bin/env python3
# Use this to import hashes from a directory into a hash database.
# Relative paths will be replaced with absolute paths.

from argparse import ArgumentParser
import subprocess
import os
import sys

if __name__=="__main__":

    parser = ArgumentParser(prog='be_import.py', description="Import block hashes recursively from files under directory 'source_dir' into hash database hashdb.hdb under new bulk_extractor directory 'be_dir'.")
    parser.add_argument('source_dir', help= 'path to the source directory')
    parser.add_argument('be_dir', help= 'path to the new bulk_extractor directory to be created')
    parser.add_argument('-p', '--block_size', type=str, default='512',
            help= 'partition size of blocks to hash, default=512')
    parser.add_argument('-a', '--sector_size', type=str, default='512',
            help= 'aligned sector boundary to scan along, default=512')
    parser.add_argument('-r', '--repository_name', type=str,
            help= "repository name, defaults to the full path to the 'source_dir' source directory provided")
    args = parser.parse_args()

    # get absolute paths
    source_dir = os.path.abspath(args.source_dir)
    be_dir = os.path.abspath(args.be_dir)

    # get repository name
    if args.repository_name is None:
        repository_name = be_dir
    else:
        repository_name = args.repository_name

    # run bulk_extractor import
    cmd = ["bulk_extractor", "-E", "hashdb",
           "-S", "hashdb_mode=import",
           "-S", "hashdb_block_size=%s" % args.block_size,
           "-S", "hashdb_import_sector_size=%s" % args.sector_size,
           "-S", "hashdb_import_repository_name=%s" % repository_name,
           "-o", be_dir,
           "-R", source_dir]

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
 
