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

    print "%s <input_folder> <output_file>" % sys.argv[0]

def main():
    """Main."""

    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)
    
    input_folder = sys.argv[1]
    output_file = sys.argv[2]

    # -------------------------------------------------------------------------
    # Done.
    
    output = ""
    
    configs = [cfg for cfg in os.listdir(input_folder) if cfg.endswith('.cfg')]
    
    # Need to have it glob the config files.
    
    for config in configs:
        config_file = os.path.join(input_folder, config)
        process = \
            subprocess.Popen(
                             ['python', 'build_frames.py', config_file],
                             shell=False,
                             stdout=subprocess.PIPE)

        output += process.communicate()[0]

    with open(output_file, 'w') as fout:
        fout.write(output)

if __name__ == "__main__":
    main()
