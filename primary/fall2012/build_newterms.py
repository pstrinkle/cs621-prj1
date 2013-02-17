#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for new terms processing.
#

import sys
import subprocess
from json import loads

import boringmatrix

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def output_new_terms(results, output):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    skey = sorted(results[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    aterms = []
    bterms = []

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        count1 = 0
        count2 = 0

        list1 = results[NOTE_BEGINS[0]][skey[idx]].term_matrix
        list2 = results[NOTE_BEGINS[1]][skey[idx]].term_matrix

        for term in list1:
            if term not in aterms:
                aterms.append(term)
                count1 += 1

        for term in list2:
            if term not in bterms:
                bterms.append(term)
                count2 += 1

        out.append("%d %d %d" % (idx, count1, count2))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'new distinct terms'\n"
    #params += "plot '%s' t '%s: %d - %d'\n" % (path, graph_title, start, end)
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, NOTE_BEGINS[0], start, end, path, NOTE_BEGINS[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."


def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        usage()
        sys.exit(-1)

    use_short_terms = False
    new_terms_out = True

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    # not building the model.
    results = None

    if model_file is None:
        sys.exit(-1)
        
    if output_name is None:
        sys.exit(-1)

    with open(model_file, 'r') as moin:
        results = loads(moin.read(), object_hook=boringmatrix.as_boring)
        # dict(loads(moin.read(), object_hook=as_boring))

    # ----------------------------------------------------------------------
    # Compute the term weights.
    for note in NOTE_BEGINS:
        # this crap only matters for the key thing.
        keys = results[note].keys()

        for idx in range(0, len(keys)):
            results[note][int(keys[idx])] = results[note][keys[idx]]
            del results[note][keys[idx]]

        for start in results[note]:
            results[note][start].compute()

#        for start in results[NOTE_BEGINS[0]]:
#            for note in NOTE_BEGINS:
#                total = 0.0
#                for term in results[note][start].term_weights:
#                    total += results[note][start].term_weights[term]
#                print total,
# 1.0 is the total weight, yay.

    print "number of slices: %d" % len(results[NOTE_BEGINS[0]])

    term_list = boringmatrix.build_termlist(results) # length of this is used to normalize
    sterm_list = boringmatrix.build_termlist2(results) # length of this is used to normalize

    print "Full Dictionary: %d" % len(term_list)
    print "Short Dictionary: %d" % len(sterm_list)

    # ----------------------------------------------------------------------
    # Prune out low term counts; re-compute.
    if use_short_terms:
        for note in results:
            for start in results[note]:
                results[note][start].drop_not_in(sterm_list)
                results[note][start].compute()

    if new_terms_out:
        output_new_terms(results, "%s_term_growth.eps" % output_name)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    