#!/usr/bin/env python3
import os
import subprocess
def _run_cmd(cmd):
    # run cmd, return lines, raise if unable to produce lines
    try:
        print("annotation reader running command: ", cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        lines = p.communicate()[0].decode('utf-8').split("\n")
    except Exception as e:
        raise RuntimeError("annoation failure running cmd: %s: %s" % (cmd, e))
    if p.returncode != 0:
        raise RuntimeError("annoation failure running cmd: "
                           "%s: lines:\n%s\nAborting." % (cmd, lines))
    return lines

def _read_mmls_annotations(media_filename, sector_size,
                                              annotation_types, annotations):
    # mmls for volume allocation table
    annotation_types.append(("mmls", "Disk partitions (from TSK mmls)", True))
    cmd = ["mmls", "-b", "%d"%sector_size, media_filename]
    lines = _run_cmd(cmd)

    for line in lines:
        # accept any line where fields parse in a valid way
        try:
            parts = line.split(None, 5)
            offset = int(parts[2]) * sector_size
            length = int(parts[4]) * sector_size
            text = parts[5]
            annotations.append(("mmls", offset, length, text))
        except Exception as e:
            # don't use this line
            pass

def _read_fsstat_annotations(media_filename, sector_size,
                                              annotation_types, annotations):

    annotation_types.append(("fsstat", "File system sectors (from TSK fsstat)",
                                                                        True))

    # tries every offset in mmls, so run _read_mmls_annotations first.

    for annotation_type, offset, _, _ in annotations:

        if annotation_type == "mmls":
            # make sure sector size is valid
            if offset % sector_size != 0:
                raise RuntimeError("annotation failure in fsstat: "
                         "sector size %s is not compatible with offset %s" %
                         (sector_size, offset))

            # calculate sector offset from offset
            sector_offset = offset // sector_size

            cmd = ["fsstat", "-b", "%d"%sector_size,
                   "-o", "%d"%sector_offset, media_filename]
            try:
                lines = _run_cmd(cmd)
            except RuntimeError as e:
                print("annotation_reader skipping fsstat byte offset %s" %
                         offset)
                lines = ""

            for line in lines:
                try:
#                    print("line.a:", line)
                    p1 = line.index('-')
                    p2 = line.index(' (')
                    p3 = line.index(')')
#                    print("line:", line, p1, p2, p3)
#                    print("o:'%s', l:'%s'" % (line[0:p1], line[p2+2:p3]))

                    # create dictionary entry for this line
                    offset= (int(line[0:p1]) + sector_offset) * sector_size
                    length = int(line[p2+2:p3]) * sector_size
                    text = line
                    annotations.append(("fsstat", offset, length, text))

                except Exception as e:
                    # don't use this line
                    pass

def read_annotations(media_filename, sector_size):
    """Read media annotations.  Throws on failure.

    Returns:
      annotation_load_status(str): "" else text if something went wrong.
      annotation_types(list<(type, description, is_active)>): Tuple of
        annotation types and whether they are active by default.
      annotations(list<(type, offset, length, text)>): List of annotations
        defined by annotation type, media offset, length, and text.
    """

    # the annotation types and the annotations to return
    annotation_load_status = ""
    annotation_types = list()
    annotations = list()

    try:

        # mmls
        _read_mmls_annotations(media_filename, sector_size,
                                               annotation_types, annotations)

        # fsstat
        _read_fsstat_annotations(media_filename, sector_size,
                                               annotation_types, annotations)

    except RuntimeError as e:
        annotation_load_status = e

    # return
    return (annotation_load_status, annotation_types, annotations)

# main
if __name__=="__main__":
    # informal test harness
    annotation_load_status, annotation_types, annotations = read_annotations(
                               "/home/bdallen/Images/charlie-2009-12-11.E01",
                                                 "/home/bdallen/Images/temp")
    print("annotations:", annotation_load_status, annotation_types, annotations)

