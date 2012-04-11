"""Running pylint with the updated pythonpath."""

import os
import sys
import subprocess

def usage():
    """."""
    
    sys.stderr.write("%s <input file>\n" % sys.argv[0])

def main():
    """."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    process = subprocess.Popen(
                             ['pylint', '--rcfile=py.config', sys.argv[1]],
                             shell=False,
                             stdout=subprocess.PIPE)

    output = process.communicate()[0]
    
    print output

    # --------------------------------------------------------------------------
    # Done.    

if __name__ == "__main__":
    main()
