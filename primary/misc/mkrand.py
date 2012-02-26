#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Stuff.
#

import sys
import random

def usage():
    sys.stderr.write("usage: %s num_val range <ouput>\n" % sys.argv[0])

def main():

    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)
    
    num_val = int(sys.argv[1])
    range_val = int(sys.argv[2])
    file_out = sys.argv[3]
    
    # uses system time
    random.seed()

    sum = 0

    with open(file_out, "w") as f:
        for i in range(num_val):
            x = random.randint(1, range_val)
            sum += x
            f.write("%d\n" % x)
    
    print "sum: %d" % sum

if __name__ == "__main__":
    main()
