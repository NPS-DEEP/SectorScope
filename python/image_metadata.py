#!/usr/bin/env python3
import os
import subprocess
import json
def _run_cmd(cmd):
    # run cmd, return lines
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    lines = p.communicate()[0].decode('utf-8').split("\n")
    if p.returncode != 0:
        print("error with command '", end="")
        print(*cmd, sep=' ', end="':\n")
        print(*lines, sep='\n')
        print("Aborting.")
        raise RuntimeError("failure running cmd.")

    return lines

def _import_mmls(image_filename, metadata_dir):
    # mmls for volume allocation table
    cmd = ["mmls", image_filename]
    lines = _run_cmd(cmd)

    outfile = os.path.join(metadata_dir, "mmls.json")
    f = open(outfile, "w")
    for line in lines:
        # accept any line where fields parse in a valid way
        try:
            parts = line.split(maxsplit=5)
            d = dict()
            d["type"] = "mmls - disk partition"
            d["offset"] = int(parts[2])*512
            d["length"] = int(parts[4])*512
            d["text"] = parts[5]
            f.write("%s\n" % json.dumps(d))
        except Exception:
            # don't use this line
            pass

def _import_metadata(image_filename, metadata_dir):
    _import_mmls(image_filename, metadata_dir)

def _read_json(metadata_file, metadata):
    f = open(metadata_file, "r")
    for line in f:
       metadata.append(json.loads(line))

def read_image_metadata(image_filename, project_dir):
    """Read image metadata from project_dir/image_metadata/ creating
      and importing if necessary."""

    metadata_dir = os.path.join(project_dir, "image_metadata")

    # create and import image metadata, if necessary
    if not os.path.exists(metadata_dir):
        os.makedirs(metadata_dir)
        _import_metadata(image_filename, metadata_dir)

    # read image metadata
    metadata = list()
    _read_json(os.path.join(metadata_dir, "mmls.json"), metadata)
    return metadata

# main
if __name__=="__main__":
    # informal test harness
    metadata = read_image_metadata(
                               "/home/bdallen/Images/charlie-2009-12-11.E01",
                                                 "/home/bdallen/Images/temp")
    print("image metadata:", metadata)

