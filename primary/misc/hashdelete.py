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
  
  for file in getFile(startpoint):
    
    if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith("Thumbs.db") or file.endswith(".gif"):
      continue
    
    if file.endswith(".png") or file.endswith(".bmp") or file.endswith("jpeg"):
      continue
    
    with open(file, "r") as f:
      sys.stderr.write(file + "\n")
      
      contents = f.read()
      h = hashlib.sha512(contents).hexdigest()
      
      if h in fileHashes:
        sys.stderr.write("possible duplicate\n")
        alen = os.stat(fileHashes[h]).st_size
        blen = os.stat(file).st_size
        
        # They're the same size.
        if alen == blen:
          f2 = open(fileHashes[h])
          contents2 = f2.read()
          f2.close()
          
          if contents == contents2:
            print "deleted: %s" % file
            #os.unlink(file)
            deleted += blen
        
      else:
        fileHashes[h] = file

  print "Deleted: %d bytes" % deleted

if __name__ == "__main__":
  main()
