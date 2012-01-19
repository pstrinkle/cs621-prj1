#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Given a path to a bunch of data files, make one points file.
#

import os
import re
import sys

def usage():
  print "usage: %s <input folder> <output file>" % sys.argv[0]
  print "\tthe files must be long lat count for this version"

def main():

  # Did they provide the correct args?
  if len(sys.argv) != 3:
    usage()
    sys.exit(-1)

  folder = sys.argv[1]
  files = os.listdir(folder)
  output = sys.argv[2]

  # ---------------------------------------------------------------------------
  # Build gnuplot input.
  
  points = {}
  
  for file in files:
    if ".data" in file:
      path = os.path.join(folder, file)
      with open(path, "r") as f:
        lines = f.readlines()
        for l in lines:
          m = re.search("(.+? .+?) (\d+?)\n", l)
          if m:
            longlat = m.group(1)
            val = int(m.group(2))
            if longlat not in points:
              points[longlat] = val
            else:
              points[longlat] += val
  
  with open(output, "w") as f:
    f.write("# lat long count\n")
    for p in points:
      f.write("%s %d\n" % (p, points[p]))

  print "len: %d" % len(points)

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
