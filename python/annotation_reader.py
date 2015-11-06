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

def _import_mmls(image_filename, annotations_dir):
    # mmls for volume allocation table
    cmd = ["mmls", image_filename]
    lines = _run_cmd(cmd)

    outfile = os.path.join(annotations_dir, "mmls.json")
    f = open(outfile, "w")
    for line in lines:
        # accept any line where fields parse in a valid way
        try:
            parts = line.split(maxsplit=5)
            d = dict()
            d["type"] = "mmls"
            d["offset"] = int(parts[2])*512
            d["length"] = int(parts[4])*512
            d["text"] = parts[5]
            f.write("%s\n" % json.dumps(d))
        except Exception:
            # don't use this line
            pass

def _import_annotations(image_filename, annotations_dir):
    _import_mmls(image_filename, annotations_dir)

def _read_json(annotations_file, annotations):
    f = open(annotations_file, "r")
    for line in f:
       d = json.loads(line)
       annotations.append((d["type"], d["offset"], d["length"], d["text"]))

def read_annotations(image_filename, project_dir):
    """Read image annotations from project_dir/annotations/ creating
      and importing if necessary.

    Returns:
      annotation_types(list<(type, description, is_active)>): Tuple of
        annotation types and whether they are active by default.
      annotations(list<(type, offset, length, text)>): List of annotations
        defined by annotation type, image offset, length, and text.
    """

    annotations_dir = os.path.join(project_dir, "annotations")

    # create and import annotations, if necessary
    if not os.path.exists(annotations_dir):
        os.makedirs(annotations_dir)
        _import_annotations(image_filename, annotations_dir)

    # read annotations
    annotation_types = list()
    annotations = list()

    # mmls
    annotation_types.append(("mmls", "Disk partitions", True))
    _read_json(os.path.join(annotations_dir, "mmls.json"), annotations)
    return (annotation_types, annotations)

# main
if __name__=="__main__":
    # informal test harness
    annotation_types, annotations = read_annotations(
                               "/home/bdallen/Images/charlie-2009-12-11.E01",
                                                 "/home/bdallen/Images/temp")
    print("annotations:", annotation_types, annotations)

