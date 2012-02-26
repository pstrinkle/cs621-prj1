#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Stuff.
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
    
    for file in getFile(startpoint):

        if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith("Thumbs.db") or file.endswith(".gif"):
            continue
                    
        if file.endswith(".png") or file.endswith(".bmp") or file.endswith("jpeg"):
            continue
            
        with open(file, "r") as f:
            sys.stderr.write(file + "\n")
                
            contents = f.read()
            h = hashlib.sha512(contents).hexdigest()
            
            try:
                fileHashes[h].append(file)
            except KeyError:
                fileHashes[h] = []
                fileHashes[h].append(file)

    for h in fileHashes:
        if len(fileHashes[h]) > 1:
            print "found possible duplicates"
            for f in fileHashes[h]:
                print "\t%s : %d" % (f, os.stat(f).st_size)
            
if __name__ == "__main__":
    main()
