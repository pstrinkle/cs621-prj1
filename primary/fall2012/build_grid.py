#! /usr/bin/python
"""Patrick Trinkle
Fall 2012
"""

__author__ = 'tri1@umbc.edu'

import sys
import subprocess

NOTE_BEGINS = ("i495", "boston")
TOPLEFT = "topleft"
TOPRIGHT = "topright"
BOTTOMLEFT = "bottomleft"
BOTTOMRIGHT = "bottomright"
XLABEL = "xlabel"
YLABEL = "ylabel"
TITLE = "title"

NEWDISTINCT = "newdistinct"
NEWPERCENTAGE = "newpercentage"
DISTINCT = "distinct"
INVENTROPY = "inventropy"
DISTINCTPERHOUR = "distinctperhour"
GNEWDISTINCT = "gnewdistinct"
GDISTINCT = "gdistinct"
GINVENTROPY = "ginventropy"

inputs = {NEWDISTINCT : "new distinct terms",
          NEWPERCENTAGE : "percentage of new distinct terms",
          DISTINCT : "how many distinct terms per interval",
          INVENTROPY : "the entropy score of each model subtracted from 1",
          DISTINCTPERHOUR : "the number of distinct terms per hour",
          GNEWDISTINCT : "how many new distinct terms per interval, top level hierarch",
          GDISTINCT : "how many distinct terms per interval, top level hierarch",
          GINVENTROPY : "the global entropy score of each model subtracted from 1"}

def dual_output(labels, ylog, output, paths):
    """title : the title.
    labels : dictionary of the labels
    ylog : boolean, should we log scale Y?
    output : the output path
    paths : dictionary of the paths."""
    
    params = "set terminal postscript eps color\n"
    params += "set output '%s.eps'\n" % output
    if ylog:
        params += "set log y\n"
    params += "set xlabel '%s'\n" % labels[XLABEL]
    params += "set ylabel '%s'\n" % labels[YLABEL]

    params += "set size 1,0.55\n"
    params += "set origin 0,0\n"
    params += "set multiplot \n"
    params += "set tmargin 2\n"

    # top left
    params += "set size 0.5,0.5\n"
    params += "set origin 0,0\n"
    params += "set title '(a)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[TOPLEFT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[TOPLEFT], NOTE_BEGINS[1])

    params += "set label '%s' at screen 0.5,0.5 center front\n" % labels[TITLE]

    # top right
    params += "set size 0.5,0.5\n"
    params += "set origin 0.5,0\n"
    params += "set title '(b)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[TOPRIGHT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[TOPRIGHT], NOTE_BEGINS[1])

    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def dual_output_single(labels, ylog, output, paths):
    """title : the title.
    labels : dictionary of the labels
    ylog : boolean, should we log scale Y?
    output : the output path
    paths : dictionary of the paths."""
    
    params = "set terminal postscript eps color\n"
    params += "set output '%s.eps'\n" % output
    if ylog:
        params += "set log y\n"
    params += "set xlabel '%s'\n" % labels[XLABEL]
    params += "set ylabel '%s'\n" % labels[YLABEL]

    params += "set size 1,0.55\n"
    params += "set origin 0,0\n"
    params += "set multiplot \n"
    params += "set tmargin 2\n"

    # top left
    params += "set size 0.5,0.5\n"
    params += "set origin 0,0\n"
    params += "set title '(a)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[TOPLEFT], 'global')

    params += "set label '%s' at screen 0.5,0.5 center front\n" % labels[TITLE]

    # top right
    params += "set size 0.5,0.5\n"
    params += "set origin 0.5,0\n"
    params += "set title '(b)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[TOPRIGHT], 'global')

    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def quad_output(labels, ylog, output, paths):
    """title : the title.
    labels : dictionary of the labels
    ylog : boolean, should we log scale Y?
    output : the output path
    paths : dictionary of the paths."""
    
    params = "set terminal postscript eps color\n"
    params += "set output '%s.eps'\n" % output
    if ylog:
        params += "set log y\n"
    params += "set xlabel '%s'\n" % labels[XLABEL]
    params += "set ylabel '%s'\n" % labels[YLABEL]
    params += "set multiplot layout 2,2 title '%s'\n" % labels[TITLE]
    params += "set tmargin 2\n"

    # top left
    params += "set title '(a)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[TOPLEFT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[TOPLEFT], NOTE_BEGINS[1])

    # top right
    params += "set title '(b)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[TOPRIGHT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[TOPRIGHT], NOTE_BEGINS[1])

    # bottom left
    params += "set title '(c)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[BOTTOMLEFT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[BOTTOMLEFT], NOTE_BEGINS[1])

    # bottom right
    params += "set title '(d)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red', " \
        % (paths[BOTTOMRIGHT], NOTE_BEGINS[0])
    params += "'%s' using 1:3 t '%s' lc rgb 'blue'\n" \
        % (paths[BOTTOMRIGHT], NOTE_BEGINS[1])

    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def quad_output_single(labels, ylog, output, paths):
    """title : the title.
    labels : dictionary of the labels
    ylog : boolean, should we log scale Y?
    output : the output path
    paths : dictionary of the paths."""
    
    params = "set terminal postscript eps color\n"
    params += "set output '%s.eps'\n" % output
    if ylog:
        params += "set log y\n"
    params += "set xlabel '%s'\n" % labels[XLABEL]
    params += "set ylabel '%s'\n" % labels[YLABEL]
    params += "set multiplot layout 2,2 title '%s'\n" % labels[TITLE]
    params += "set tmargin 2\n"

    # top left
    params += "set title '(a)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[TOPLEFT], 'global')

    # top right
    params += "set title '(b)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[TOPRIGHT], 'global')

    # bottom left
    params += "set title '(c)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[BOTTOMLEFT], 'global')

    # bottom right
    params += "set title '(d)'\n"
    params += "plot '%s' using 1:2 t '%s' lc rgb 'red'\n" \
        % (paths[BOTTOMRIGHT], 'global')

    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def usage():
    """Print the massive usage information."""

    usg = \
"""usage: %s -type <type> -out <output> [-globals] \
-tl <topleft> -tr <topright> \
-bl <bottomleft> -br <bottomright>

-type the type you want to output
-out the output path and name, leave off eps
-globals we're outputing global lines, so use quad_single().

For a 2-tile grid, supply only topleft and topright, otherwise supply all four.

types:
"""
    sys.stderr.write(usg % sys.argv[0])
    
    for value in inputs:
        sys.stderr.write("\t%s as type for outputing %s.\n" \
                         % (value, inputs[value]))

def main():
    """."""
    
    # Did they provide the correct args?
    if len(sys.argv) < 9 or len(sys.argv) > 14:
        usage()
        sys.exit(-1)

    paths = {}

    labelsets = {
        NEWDISTINCT : {TITLE : "Distinct New Terms per Interval",
                       XLABEL : "t",
                       YLABEL : "new distinct terms"},
        NEWPERCENTAGE : {TITLE : "Percentage of Distinct New Terms per Interval",
                         XLABEL : "t",
                         YLABEL : "percentage of new terms"},
        DISTINCT : {TITLE : "Distinct Terms per Interval",
                    XLABEL : "t",
                    YLABEL : "distinct terms"},
        INVENTROPY : {TITLE : "1-Entropy per Interval",
                      XLABEL : "t",
                      YLABEL : "nats"},
        DISTINCTPERHOUR : {TITLE : "Number of Distinct Terms per Hour",
                           XLABEL : "hour",
                           YLABEL : "distinct terms"},
        GNEWDISTINCT : {TITLE : "New Terms in Top-Level Hierarchical Model per Interval",
                        XLABEL : "t",
                        YLABEL : "new distinct terms"},
        GDISTINCT : {TITLE : "Distinct Terms in Top-Level Hierarchical per Interval",
                     XLABEL : "t",
                     YLABEL : "distinct terms"},
        GINVENTROPY : {TITLE : "1-Entropy of Top-Level Hierarchical per Interval",
                       XLABEL : "t",
                       YLABEL : "nats"}}

    output_type = None
    output = None
    use_single_out = False
    
    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-type" == sys.argv[idx]:
                output_type = sys.argv[idx + 1]
            if "-out" == sys.argv[idx]:
                output = sys.argv[idx + 1]
            if "-globals" == sys.argv[idx]:
                use_single_out = True
            if "-tl" == sys.argv[idx]: 
                paths[TOPLEFT] = sys.argv[idx + 1]
            elif "-tr" == sys.argv[idx]:
                paths[TOPRIGHT] = sys.argv[idx + 1]
            elif "-bl" == sys.argv[idx]:
                paths[BOTTOMLEFT] = sys.argv[idx + 1]
            elif "-br" == sys.argv[idx]:
                paths[BOTTOMRIGHT] = sys.argv[idx + 1]
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    if output_type is None or output is None:
        usage()
        sys.exit(-1)

    if len(paths) != 2 and len(paths) != 4:
        usage()
        sys.exit(-1)

    # if you provided the wrong input, you'll get a KeyError exception.

    try:
        labels = labelsets[output_type]
    except KeyError:
        usage()
        sys.exit(-1)

    logy = False

    if output_type == NEWDISTINCT:
        logy = True

    if len(paths) == 2:
        if use_single_out:
            dual_output_single(labels, logy, output, paths)
        else:
            dual_output(labels, logy, output, paths)
    else:
        if use_single_out:
            quad_output_single(labels, logy, output, paths)
        else:
            quad_output(labels, logy, output, paths)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()