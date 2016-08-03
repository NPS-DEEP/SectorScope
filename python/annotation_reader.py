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
        raise RuntimeError("failure running cmd: %s: lines:\n%s\nAborting." %
                           (cmd, lines))

    return lines

def _import_mmls(media_filename, annotation_dir):
    # mmls for volume allocation table
    cmd = ["mmls", media_filename]
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

def _import_fsstat(media_filename, annotation_dir):
    # fsstat file system statistics, specifically, allocated sectors

    # first, get partition information from the volume system
    cmd = ["mmls", media_filename]
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
    with open(outfile, "w") as f:
        for sector_offset in partition_starts:
            try:
                cmd = ["fsstat", "-o", "%s"%sector_offset, media_filename]
                lines = _run_cmd(cmd)
            except RuntimeError as e:
                # skip partition if it has no file system
                print("Annotation reader: Skipping fsstat offset %s" %
                                                            sector_offset)
                continue
            print("Annotation reader: Importing fsstat offset %s" %
                                                            sector_offset)
            for line in lines:
                try:
#                    print("line.a:", line)
                    p1 = line.index('-')
                    p2 = line.index(' (')
                    p3 = line.index(')')
#                    print("line:", line, p1, p2, p3)
#                    print("o:'%s', l:'%s'" % (line[0:p1], line[p2+2:p3]))

                    # create dictionary entry for this line
                    d = dict()
                    d["type"] = "fsstat"
                    d["offset"] = (int(line[0:p1]) + sector_offset) * 512
#                    print("off", d["offset"])
                    d["length"] = int(line[p2+2:p3]) * 512
#                    print("len", d["length"])
                    d["text"] = line
                    f.write("%s\n" % json.dumps(d))

                except Exception:
                    # don't use this line
                    pass

def _import_annotations(media_filename, annotation_dir):
    print("Annotation reader: importing mmls annotations...")
    _import_mmls(media_filename, annotation_dir)
    print("Annotation reader: importing fsstat annotations...")
    _import_fsstat(media_filename, annotation_dir)

    # record media_filename in annotation_dir
    print("Annotation reader: recording media image filename...")
    media_filename_path = os.path.join(annotation_dir, "media_filename")
    with open(media_filename_path, "w") as f:
        f.write("%s\n" % media_filename)

def _read_json(annotations_file, annotations):
    with open(annotations_file, "r") as f:
        for line in f:
            d = json.loads(line)
            annotations.append((d["type"], d["offset"], d["length"], d["text"]))

def read_annotations(media_filename, annotation_dir):
    """Read media annotations from annotation_dir, creating them if necessary.
    Throws on failure.

    Returns:
      annotation_types(list<(type, description, is_active)>): Tuple of
        annotation types and whether they are active by default.
      annotations(list<(type, offset, length, text)>): List of annotations
        defined by annotation type, media offset, length, and text.
    """

    # check status of annotation_dir
    if not os.path.exists(annotation_dir):
        # create annotation_dir and import annotations
        os.makedirs(annotation_dir)
        _import_annotations(media_filename, annotation_dir)
    else:
        # make sure annotation_dir is right for this media image
        media_filename_path = os.path.join(annotation_dir, "media_filename")
        with open(media_filename_path, 'r') as f:
            line = f.readline().strip()
            if os.path.abspath(line) != os.path.abspath(media_filename):
                raise ValueError("Incorrect media filename in pre-built"
                        " annotation directory.  Expected %s"
                        " but found %s" % (os.path.abspath(media_filename),
                        os.path.abspath(line)))

    # read annotations
    annotation_types = list()
    annotations = list()

    # mmls
    print("Annotation reader: reading mmls annotations...")
    annotation_types.append(("mmls", "Disk partitions (from TSK mmls)", True))
    _read_json(os.path.join(annotation_dir, "mmls.json"), annotations)

    # fsstat
    print("Annotation reader: reading fsstat annotations...")
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

