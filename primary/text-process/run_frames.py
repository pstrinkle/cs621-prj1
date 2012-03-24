#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: Runs build_frames.py with varied parameters.
#

import os
import sys
import subprocess

sys.path.append(os.path.join("..", "tweetlib"))
import tweetdate

def usage():
    """Standard usage message."""

    print "%s <output_file>" % sys.argv[0]

    return

def main():
    """Main."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)
    
    output_file = sys.argv[1]

    # -------------------------------------------------------------------------
    # Done.
    
    output = ""
    
    configs = \
        ('2011_jul_100_rm.cfg', '2011_jul_150_rm.cfg', '2011_jul_250_rm.cfg')
    
    # Need to have it glob the config files.
    
    for config in configs:
        process = \
            subprocess.Popen(
                             ['python', 'build_frames.py', config],
                             shell=False,
                             stdout=subprocess.PIPE)

        output += process.communicate()[0]

    with open(output_file, 'w') as fout:
        fout.write(output)

if __name__ == "__main__":
    main()
