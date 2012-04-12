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
            if file[0] != ".":
                yield os.path.join(root, file)

def usage():
    sys.stderr.write("usage: %s path\n" % sys.argv[0])

def main():

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    startpoint = sys.argv[1]
    fileHashes = {}
    
    path_disqualifiers = (".jpg", ".JPG", "Thumbs.db", ".gif", ".png", ".bmp", 
                          "jpeg")
    
    for path in getFile(startpoint):
        
        if path.endswith(path_disqualifiers):
            continue

        with open(path, "r") as fin:
            sys.stderr.write(path + "\n")
            contents = fin.read(20 * 1024)
            h = hashlib.sha512(contents).hexdigest()
            
            value = "%s : %d" % (path, os.stat(path).st_size)
            
            try:
                fileHashes[h].append(value)
            except KeyError:
                fileHashes[h] = []
                fileHashes[h].append(value)

    for h in fileHashes:
        if len(fileHashes[h]) > 1:
            print "found possible duplicates:"
            for f in fileHashes[h]:
                print "\t%s" % f
            
if __name__ == "__main__":
    main()
