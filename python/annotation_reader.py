#!/usr/bin/env python3
import os
import subprocess
import json
def _run_cmd(cmd):
    # run cmd, return lines
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines = p.communicate()[0].decode('utf-8').split("\n")
    except Exception as e:
        raise RuntimeError("failure running cmd: %s: %s" % (cmd, e))
    if p.returncode != 0:
#        print("error with command '", end="")
#        print(*cmd, sep=' ', end="':\n")
#        print(*lines, sep='\n')
        print("error with command:")
        print(cmd)
        print(lines)
        print("Aborting.")
        raise RuntimeError("failure running cmd: %s" % cmd)

    return lines

def _import_mmls(image_filename, annotation_dir):
    # mmls for volume allocation table
    cmd = ["mmls", image_filename]
    lines = _run_cmd(cmd)

    outfile = os.path.join(annotation_dir, "mmls.json")
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

def _import_fsstat(image_filename, annotation_dir):
    # fsstat file system statistics, specifically, allocated sectors

    # first, get partition information
    cmd = ["mmls", image_filename]
    lines = _run_cmd(cmd)

    # find any line where fields parse in a valid way
    partition_starts = list()
    for line in lines:
        try:
            parts = line.split(maxsplit=5)
            sector_offset = int(parts[2])
            partition_starts.append(sector_offset)
        except Exception:
            # don't use this line
            pass


    # now run fsstat on each partition start
    outfile = os.path.join(annotation_dir, "fsstat.json")
    f = open(outfile, "w")
    for sector_offset in partition_starts:
        try:
            cmd = ["fsstat", "-o", "%s"%sector_offset, image_filename]
            lines = _run_cmd(cmd)
        except RuntimeError:
            # skip partition if it has no file system
            continue
        for line in lines:
            try:
#                print("line.a:", line)
                p1 = line.index('-')
                p2 = line.index(' (')
                p3 = line.index(')')
#                print("line:", line, p1, p2, p3)
#                print("o:'%s', l:'%s'" % (line[0:p1], line[p2+2:p3]))

                # create dictionary entry for this line
                d = dict()
                d["type"] = "fsstat"
                d["offset"] = int(line[0:p1]) * 512
#                print("off", d["offset"])
                d["length"] = int(line[p2+2:p3]) * 512
#                print("len", d["length"])
                d["text"] = line
                f.write("%s\n" % json.dumps(d))

            except Exception:
                # don't use this line
                pass

def _import_annotations(image_filename, annotation_dir):
    _import_mmls(image_filename, annotation_dir)
    _import_fsstat(image_filename, annotation_dir)

    # record image_filename in annotation_dir
    image_filename_path = os.path.join(annotation_dir, "image_filename")
    f = open(image_filename_path, "w")
    f.write("%s\n" % image_filename)

def _read_json(annotations_file, annotations):
    f = open(annotations_file, "r")
    for line in f:
       d = json.loads(line)
       annotations.append((d["type"], d["offset"], d["length"], d["text"]))

def read_annotations(image_filename, annotation_dir):
    """Read image annotations from annotation_dir, creating them if necessary.
    Throws on failure.

    Returns:
      annotation_types(list<(type, description, is_active)>): Tuple of
        annotation types and whether they are active by default.
      annotations(list<(type, offset, length, text)>): List of annotations
        defined by annotation type, image offset, length, and text.
    """

    # check status of annotation_dir
    if not os.path.exists(annotation_dir):
        # create annotation_dir and import annotations
        os.makedirs(annotation_dir)
        _import_annotations(image_filename, annotation_dir)
    else:
        # make sure annotation_dir is right for this media image
        image_filename_path = os.path.join(annotation_dir, "image_filename")
        with open(image_filename_path, 'r') as f:
            line = f.readline().strip()
            if os.path.abspath(line) != os.path.abspath(image_filename):
                raise ValueError("Incorrect image filename in pre-built"
                        " annotation directory.  Expected %s"
                        " but found %s" % (os.path.abspath(image_filename),
                        os.path.abspath(line)))

    # read annotations
    annotation_types = list()
    annotations = list()

    # mmls
    annotation_types.append(("mmls", "Disk partitions (from TSK mmls)", True))
    _read_json(os.path.join(annotation_dir, "mmls.json"), annotations)

    # fsstat
    annotation_types.append(("fsstat", "File system sectors (from TSK fsstat)",
                                                                        True))
    _read_json(os.path.join(annotation_dir, "fsstat.json"), annotations)

    # return
    return (annotation_types, annotations)

# main
if __name__=="__main__":
    # informal test harness
    annotation_types, annotations = read_annotations(
                               "/home/bdallen/Images/charlie-2009-12-11.E01",
                                                 "/home/bdallen/Images/temp")
    print("annotations:", annotation_types, annotations)

