#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
#
# @summary: Stuff.
#

import os
import sys
import hashlib

# This returns hidden files as well.
def getFile(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            yield os.path.join(root, file)

def usage():
    sys.stderr.write("usage: %s path\n" % sys.argv[0])

def main():

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    startpoint = sys.argv[1]
    fileHashes = {}
    
    for path in getFile(startpoint):

        if path.endswith(".jpg") or path.endswith(".JPG") or path.endswith("Thumbs.db") or path.endswith(".gif"):
            continue
                    
        if path.endswith(".png") or path.endswith(".bmp") or path.endswith("jpeg"):
            continue
            
        with open(path, "r") as f:
            sys.stderr.write(path + "\n")
                
            contents = f.read()
            h = hashlib.sha512(contents).hexdigest()
            
            try:
                fileHashes[h].append(path)
            except KeyError:
                fileHashes[h] = []
                fileHashes[h].append(path)

    for h in fileHashes:
        if len(fileHashes[h]) > 1:
            print "found possible duplicates"
            for f in fileHashes[h]:
                print "\t%s : %d" % (f, os.stat(f).st_size)
            
if __name__ == "__main__":
    main()
