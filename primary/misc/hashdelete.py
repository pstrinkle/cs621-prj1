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
    deleted = 0
    
    for path in getFile(startpoint):
        
        if path.endswith(".jpg") or path.endswith(".JPG") or path.endswith("Thumbs.db") or path.endswith(".gif"):
            continue
        
        if path.endswith(".png") or path.endswith(".bmp") or path.endswith("jpeg"):
            continue
        
        with open(path, "r") as f:
            sys.stderr.write(path + "\n")
            
            contents = f.read()
            h = hashlib.sha512(contents).hexdigest()
            
            if h in fileHashes:
                sys.stderr.write("possible duplicate\n")
                alen = os.stat(fileHashes[h]).st_size
                blen = os.stat(path).st_size
                
                # They're the same size.
                if alen == blen:
                    f2 = open(fileHashes[h])
                    contents2 = f2.read()
                    f2.close()
                    
                    if contents == contents2:
                        print "deleted: %s" % path
                        #os.unlink(path)
                        deleted += blen
                
            else:
                fileHashes[h] = path

    print "Deleted: %d bytes" % deleted

if __name__ == "__main__":
    main()
