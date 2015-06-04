#!/usr/bin/env python3
# coding=UTF-8
# 
# identified_data_reader.py:
# A module for reading data from or derived from identified_blocks.txt

"""
Module for reading data from or derived from identified_blocks.txt
"""


__version__ = "0.0.1"

b'This module needs Python 2.7 or later.'
import os
import xml
import json

#def is_hashdb_dir(hashdb_dir):
#        # make sure report.xml is there
#        if os.path.exists(be_report_file)
#            print("aborting, no settings.xml at path:", filename)
#            exit(1)
#
#    return os.path.exists(os.path.join(hashdb_dir, 'settings.xml'))


class IdentifiedData():
    def __init__(self, be_report_file):

        self.be_dir = os.path.dirname(be_report_file)

        # read report_file.xml
        report_file_dict = read_report_file(be_report_file)
        self.image_size = report_file_dict.image_size
        self.image_filename = report_file_dict.image_filename
        self.hashdb_dir = report_file_dict.hashdb_dir

        # make identified_blocks_expanded.txt file
        maybe_make_identified_blocks_expanded_file()

        # read identified_blocks.txt
        (self.identified_blocks, self.identified_sources) =
                         read_identified_blocks(
                         os.path.join(self.be_dir, 'identified_blocks.txt'))

    def _maybe_make_identified_blocks_expanded_file():
        identified_blocks_expanded_file = os.path.join(
                            self.be_dir, 'identified_blocks_expanded.txt'))
        if not os.path.exists(identified_blocks_expanded_file)
            # make the file
            cmd = list({"hashdb", "expand_identified_blocks",
                        self.hashdb_dir, identified_blocks_expanded_file})

 
    def _read_report_file(be_report_file):
        """read information from report.xml into a dictionary"""
        report_file_dict = dict()

        if not os.path.exists(be_report_file):
            print("%s does not exist" % be_report_file)
            exit(1)
        xmldoc = xml.dom.minidom.parse(open(be_report_file, 'r'))

        # image size
        image_size = int((xmldoc.getElementsByTagName(
                                     "image_size")[0].firstChild.wholeText))
        report_file_dict["image_size"] = image_size

        # image filename
        image_filename = xmldoc.getElementsByTagName(
                           "image_filename")[0].firstChild.wholeText
        report_file_dict["image_filename"] = image_filename

        # hashdb_dir from command_line tag
        command_line = xmldoc.getElementsByTagName(
                           "command_line")[0].firstChild.wholeText
        i = command_line.find('hashdb_scan_path_or_socket=')
        if i is -1:
            print("aborting, hash database not found in report.xml")
            exit(1)
        i += 28
        if command_line[i] is b'"':
            # db is quoted
            i += 1
            i2 = command_line.find(b'"', i)
            if i2 is -1
                print("aborting, close quote not found in report.xml")
                exit(1)
            report_file_dict["hashdb_dir"] = command_line[i:i2]
        else:
            # db is quoted so take text to next space
            i2 = command_line.find(b' ', i)
            if i2 is -1:
                report_file_dict["hashdb_dir"] = command_line[i:]
            else:
                report_file_dict["hashdb_dir"] = command_line[i:i2]

        return report_file_dict

    def _read_identified_blocks_expanded(identified_blocks_file):
        """Read identified_blocks_expanded.txt into hash and source dictionaries
        """

        # read each line
        identified_blocks=dict()
        identified_sources=dict()
        with open(identified_blocks_file, 'r') as f:
            i = 0
            for line in f:
                try:
                    i++
                    if line[0]=='#' or len(line)==0:
                        continue

                    # get line parts
                    (forensic_path, sector_hash, fields) = line.split("\t")

                    # get source information from fields
                    fields = json.loads(fields)
                    sources = list()
                    for source in fields.sources:
                        sources.append(source.source_id, source.file_offset)

                        # also add source to identified sources
                        if source.filename not None:
                            identified_sources[source.source_id]=source

                    # add feature entry to identified_blocks
                    identified_blocks[forensic_path]=(sector_hash, sources)

                except ValueError:
                    print("Error in line ", i, ": '%s'" %line)
                    continue
            return (identified_blocks, identified_sources)


def be_version(exe):
    """Returns the version number for a bulk_extractor executable"""
    from subprocess import Popen,PIPE
    return Popen([exe,'-V'],stdout=PIPE).communicate()[0].decode('utf-8').split(' ')[1].strip()

def decode_feature(ffmt):
    """Decodes a feature in a feature file into Unicode"""
    tbin = ffmt.decode('unicode_escape')
    bin = tbin.encode('latin1')
    if b"\000" in bin:
        # If it has a \000 in it, must be UTF-16
        try:
            return bin.decode('utf-16-le')
        except UnicodeDecodeError:
            return tbin
    try:
        return bin.decode('utf-8')
    except UnicodeDecodeError:
        pass
    try:
        return bin.decode('utf-16-le')
    except UnicodeDecodeError:
        pass
    return tbin
    
    
def is_comment_line(line):
    if len(line)==0: return False
    if line[0:4]==b'\xef\xbb\xbf#': return True
    if line[0:1]=='\ufeff':
        line=line[1:]       # ignore unicode BOM
    try:
        if ord(line[0])==65279:
            line=line[1:]       # ignore unicode BOM
    except TypeError:
        pass
    if line[0:1]==b'#' or line[0:1]=='#':
        return True
    return False

def is_histogram_line(line):
    return line[0:2]==b"n="

def get_property_line(line):
    """If it is a property line return the (property, value)"""
    if line[0:1]=='#':
        m = property_re.search(line)
        if m:
            return (m.group(1),m.group(2))
    return None

def parse_feature_line(line):
    """Determines if LINE is a line from a feature file. If it is not, return None.
    LINE must be binary.
    If it is, return the fields.
    Previously this assumed that line was in binary; now it assumes that line is in text.
    """
    if len(line)<2: return None
    if line[0]==b'#': return None # can't parse a comment
    if line[-1:]==b'\r': line=line[:-1] # remove \r if it is present (running on Windows?)
    ary = line.split(b"\t")
    
    # Should have betwen 3 fields (standard feature file)
    # and no more than 

    if len(ary)<MIN_FIELDS_PER_FEATURE_FILE_LINE or len(ary)>MAX_FIELDS_PER_FEATURE_FILE_LINE:
        # Don't know
        return None
    if b"\xf4\x80\x80\x9c" in ary[0]: return ary # contains files
    if len(ary[0])<1: return None
    if ary[0][0]<ord('0') or ary[0][0]>ord('9'): return None
    return ary

def is_feature_line(line):
    if parse_feature_line(line):
        return True
    else:
        return False

def is_histogram_filename(fname):
    """Returns true if this is a histogram file"""
    if "_histogram" in fname: return True
    if "url_" in fname: return True # I know this is a histogram file
    if fname=="ccn_track2.txt": return False # I know this is not
    return None                              # don't know

def is_feature_filename(fname):
    """Returns true if this is a feature file"""
    if not fname.endswith(".txt"): return False
    if "/" in fname: return False # must be in root directory
    if "_histogram" in fname: return False
    if "_stopped" in fname: return False
    if "_tags" in fname: return False
    if "wordlist" in fname: return False
    #if "alerts.txt" in fname: return False
    return None                 # don't know


class BulkReport:
    """Creates an object from a bulk_extractor report. The report can be a directory or a ZIP of a directory.
    Methods that you may find useful:
    f = b.open(fname,mode) - opens the file f and returns a file handle. mode defaults to 'r'
    b.is_histogram_file(fname) - returns if fname is a histogram file or not
    b.image_filename() - Returns the name of the image file
    b.read_histogram(fn) - Reads a histogram and returns the histogram
    b.histogram_files()     - Set of histogram names
    b.feature_files()   
    b.files   - Set of all files
    b.get_features(fname)   - just get the features
"""    

    def __init__(self,fn,do_validate=True):
        self.commonprefix=''
        def validate():
            """Validates the XML and finds the histograms and feature files"""
            import xml.dom.minidom
            import xml.parsers.expat
            try:
                self.xmldoc = xml.dom.minidom.parse(self.open("report.xml"))
            except xml.parsers.expat.ExpatError as e:
                raise IOError("Invalid or missing report.xml file. specify do_validate=False to avoid validation")
            return True

        import os.path,glob
        self.name  = fn
        if os.path.isdir(fn):
            self.zipfile = None
            self.dname = fn
            self.all_files = set([os.path.basename(x) for x in glob.glob(os.path.join(fn,"*"))])
            self.files = set([os.path.basename(x) for x in glob.glob(os.path.join(fn,"*.txt"))])
            if do_validate: validate()
            return

        if fn.endswith(".zip") and os.path.isfile(fn):
            self.zipfile = zipfile.ZipFile(fn)
            
            # If there is a common prefix, we'll ignore it in is_feature_file()
            self.commonprefix = os.path.commonprefix(self.zipfile.namelist())
            while len(self.commonprefix)>0 and self.commonprefix[-1]!='/':
                self.commonprefix=self.commonprefix[0:-1]

            # first find the report.xml file. If we find it, then we want to remove what comes before from
            # each name in the map.
            report_name_list = list(filter(lambda f:f.endswith("report.xml"), self.zipfile.namelist()))
            report_name_prefix = None
            if report_name_list:
                report_name_prefix = report_name_list[0].replace("report.xml","")

            # extract the filenames and make a map from short name to long name.
            self.files = set()
            self.map   = dict()
            for fn in self.zipfile.namelist():
                short_fn = fn
                if report_name_prefix:
                    short_fn = fn.replace(report_name_prefix,"")
                self.files.add(short_fn)
                self.map[short_fn] = fn
            if do_validate: validate()
            return
        if fn.endswith(".txt"):
            import sys
            print("***\n*** {} ends with .txt\n*** BulkReader wants the report directory, not the individual feature file\n***".format(fn))
        raise RuntimeError("Cannot process " + fn)

    def image_filename(self):
        """Returns the file name of the disk image that was used."""
        return self.xmldoc.getElementsByTagName("image_filename")[0].firstChild.wholeText

    def version(self):
        """Returns the version of bulk_extractor that made the file."""
        return self.xmldoc.getElementsByTagName("version")[0].firstChild.wholeText

    def threads(self):
        """Returns the number of threads used for scanning."""
        return int((self.xmldoc.getElementsByTagName("configuration")[0]
                .getElementsByTagName("threads")[0].firstChild.wholeText))

    def page_size(self):
        """Returns the size of each page processed."""
        return int((self.xmldoc.getElementsByTagName("configuration")[0]
                .getElementsByTagName("pagesize")[0].firstChild.wholeText))

    def margin_size(self):
        """Returns the size of the overlapping margins around each page."""
        return int((self.xmldoc.getElementsByTagName("configuration")[0]
                .getElementsByTagName("marginsize")[0].firstChild.wholeText))

    def clocktime(self):
        """Returns the total real time elapsed for this run.  Values are truncated to the second."""
        return int(float((self.xmldoc.getElementsByTagName("rusage")[0]
                .getElementsByTagName("clocktime")[0].firstChild.wholeText)))

    def peak_memory(self):
        """Returns the maximum memory allocated for this run."""
        return int((self.xmldoc.getElementsByTagName("rusage")[0]
                .getElementsByTagName("maxrss")[0].firstChild.wholeText))

    def open(self,fname,mode='r'):
        """Opens a named file in the bulk report. Default is text mode.
        """
        # zipfile always opens in Binary mode, but generates an error
        # if the 'b' is present, so remove it if present.
        if self.zipfile:
            mode = mode.replace("b","")
            f = self.zipfile.open(self.map[fname],mode=mode)
        else:
            mode = mode.replace("b","")+"b"
            fn = os.path.join(self.dname,fname)
            f = open(fn,mode=mode)
        return f

    def count_lines(self,fname):
        count = 0
        for line in self.open(fname):
            if not is_comment_line(line):
                count += 1
        return count
        
    def is_histogram_file(self,fn):
        if is_histogram_filename(fn)==True: return True
        for line in self.open(fn,'r'):
            if is_comment_line(line): continue
            return is_histogram_line(line)
        return False

    def feature_file_name(self,fn):
        """Returns the name of the feature file name (fn may be the full path)"""
        if fn.startswith(self.commonprefix):
            return fn[len(self.commonprefix):]
        return fn

    def is_feature_file(self,fn):
        """Return true if fn is a feature file"""
        if is_feature_filename(self.feature_file_name(fn))==False:
            return False
        for line in self.open(fn):
            if is_comment_line(line): continue
            return is_feature_line(line)
        return False
        
    def histogram_files(self):
        """Returns a list of the histograms, by name"""
        return filter(lambda fn:self.is_histogram_file(fn),self.files)

    def feature_files(self):
        """Returns a list of the feature_files, by name"""
        return sorted(filter(lambda fn:self.is_feature_file(fn),self.files))

    def carved_files(self):
        return sorted(filter(lambda fn:"/" in fn,self.files))

    def read_histogram_entries(self,fn):
        """Read a histogram file and return a dictonary of the histogram. Removes \t(utf16=...) """
        import re
        r = re.compile(b"^n=(\d+)\t(.*)$")
        for line in self.open(fn,'r'):
            # line = line.decode('utf-8')
            m = r.search(line)
            if m:
                k = m.group(2)
                p = k.find(b"\t")
                if p>0: k = k[0:p]
                yield (k,int(m.group(1)))


    def read_histogram(self,fn):
        """Read a histogram file and return a dictonary of the histogram. Removes \t(utf16=...) """
        ret = {}
        for (k,v) in self.read_histogram_entries(fn):
            ret[k] = int(v)
        return ret

    def read_features(self,fname):
        """Just read the features out of a feature file"""
        """Usage: for (pos,feature,context) in br.read_features("fname")"""
        for line in self.open(fname,"rb"):
            r = parse_feature_line(line)
            if r:
                yield r
        
        
if(__name__=='__main__'):
    from optparse import OptionParser
    global options
    import os

    parser = OptionParser()
    parser.add_option("--wordlist",help="split a wordlist.txt file")
    (options,args) = parser.parse_args()

    if options.wordlist:
        global counter
        fn = options.wordlist
        if not os.path.exists(fn):
            print("%s does not exist" % fn)
            exit(1)
        print("Splitting wordlist file %s" % fn)
        fntemp = fn.replace(".txt","_%03d.txt")
        counter = 0
        seen = set()

        def next_file():
            global counter
            nfn = fntemp % counter
            counter += 1
            print("Switching to file %s" % nfn) 
            return open(nfn,"w")

        f = next_file()
        size = 0
        max_size = 1000*1000*10
        for line in open(fn,"r"):
            word = line.split("\t")[1]
            if word not in seen:
                f.write(word)
                if word[-1]!='\n': f.write("\n")
                seen.add(word)
                size += len(word)+1
                if size>max_size:
                    f.close()
                    f = next_file()
                    size = 0
