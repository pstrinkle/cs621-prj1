#! /usr/bin/python
"""Patrick Trinkle
Fall 2012



set terminal postscript eps color
set output 'tmp.eps'
unset key
set log xy
set xlabel 'km from centroid'
set ylabel '# occurrences'

set size 1,1
set origin 0,0
set multiplot

set size 0.5,0.5
set origin 0,0
set title '(c)'
plot '14069546_geo_distcnt.data'

set size 0.5,0.5
set origin 0.5,0
set title '(d)'
plot '32405545_geo_distcnt.data'

set size 0.5,0.5
set origin 0,0.5
set title '(a)'
plot '333453889_geo_distcnt.data'

set size 0.5,0.5
set origin 0.5,0.5
set title '(b)'
plot '35263_geo_distcnt.data'

unset multiplot
set term x11
set output

"""

__author__ = 'tri1@umbc.edu'

import sys
import subprocess

NOTE_BEGINS = ("i495", "boston")

def new_terms(output, topleft, topright, bottomleft, bottomright):
    """TL := top left, TR := top right, LL := lower left, LR := lower right
    
    Need to maybe work on titles."""
    
    title = "Number of Distinct New Terms per Interval"
    
    # distinct terms.
    params = "set terminal postscript eps color\n"
    params += "set output '%s'\n" % output
    params += "set log y\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'new distinct terms'\n"
    params += "set multiplot layout 2,2 title '%s'\n" % title
    params += "set tmargin 2\n"

    # top left
    params += "set title '(a)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " % (topleft, NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" % (topleft, NOTE_BEGINS[1])

    # top right
    params += "set title '(b)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " % (topright, NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" % (topright, NOTE_BEGINS[1])

    # bottom left
    params += "set title '(c)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " % (bottomleft, NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" % (bottomleft, NOTE_BEGINS[1])

    # bottom right
    params += "set title '(d)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " % (bottomright, NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" % (bottomright, NOTE_BEGINS[1])

    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def usage():
    """Print the massive usage information."""

    usg = \
"""usage: %s -type <type> -out <output> \
-tl <topleft> -tr <topright> \
-bl <bottomleft> -br <bottomright>


newdistinct as type for outputing new distinct terms."""
    sys.stderr.write(usg % sys.argv[0])

def main():
    """."""
    
    # Did they provide the correct args?
    if len(sys.argv) != 13:
        usage()
        sys.exit(-1)
    
    topleft = None
    topright = None
    bottomleft = None
    bottomright = None
    output_type = None
    output = None

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-type" == sys.argv[idx]:
                output_type = sys.argv[idx + 1]
            if "-out" == sys.argv[idx]:
                output = sys.argv[idx + 1]
            if "-tl" == sys.argv[idx]:
                topleft = sys.argv[idx + 1]
            elif "-tr" == sys.argv[idx]:
                topright = sys.argv[idx + 1]
            elif "-bl" == sys.argv[idx]:
                bottomleft = sys.argv[idx + 1]
            elif "-br" == sys.argv[idx]:
                bottomright = sys.argv[idx + 1]
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    if output_type is None or output is None:
        usage()
        sys.exit(-1)

    if topleft is None or topright is None:
        usage()
        sys.exit(-1)
    
    if bottomleft is None or bottomright is None:
        usage()
        sys.exit(-1)
    
    if output_type == "newdistinct":
        new_terms(output, topleft, topright, bottomleft, bottomright)
    else:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()