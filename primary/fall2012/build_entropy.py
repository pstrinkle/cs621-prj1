#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for entropy processing.
#

import os
import sys
import random
import subprocess
from json import dumps, loads
from math import log

import boringmatrix

sys.path.append("../modellib")
import vectorspace

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def output_basic_entropy(entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[NOTE_BEGINS[0]][skey[idx]],
                                 entropies[NOTE_BEGINS[1]][skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy scores'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, NOTE_BEGINS[0], start, end, path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_inverse_entropy(entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        val1 = entropies[NOTE_BEGINS[0]][skey[idx]]
        val2 = entropies[NOTE_BEGINS[1]][skey[idx]]

        if val1 > 0.0:
            out1 = 1.0 - val1
        else:
            out1 = 0.0

        if val2 > 0.0:
            out2 = 1.0 - val2
        else:
            out2 = 0.0

        out.append("%d %f %f" % (idx, out1, out2))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel '(1 - entropy) scores'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, NOTE_BEGINS[0], start, end, path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_top_model_entropy(results, entropies, output):
    """Go through the entropy values and output the top terms from the models, 
    when the entropy goes low beyond some threshold."""
    
    output_model = {}
    
    # entropies[NOTE_BEGINS[0]][start] = basic_entropy()
    # results[note][start] = boringmatrix.BoringMatrix()
    skey = sorted(entropies[NOTE_BEGINS[0]].keys())

    for idx in range(0, len(skey)):
        val1 = entropies[NOTE_BEGINS[0]][skey[idx]]
        val2 = entropies[NOTE_BEGINS[1]][skey[idx]]

        if val1 > 0.0:
            out1 = 1.0 - val1
        else:
            out1 = 0.0

        if val2 > 0.0:
            out2 = 1.0 - val2
        else:
            out2 = 0.0

        if out1 > 0.05 or out2 > 0.05:
            output_model[skey[idx]] = (vectorspace.top_terms(results[NOTE_BEGINS[0]][skey[idx]].term_weights, 10),
                                       vectorspace.top_terms(results[NOTE_BEGINS[1]][skey[idx]].term_weights, 10))

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))


#### Unused
def output_renyi_entropy(alpha, entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[NOTE_BEGINS[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[NOTE_BEGINS[0]][skey[idx]],
                                 entropies[NOTE_BEGINS[1]][skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'renyi scores - %f'\n" % alpha
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, NOTE_BEGINS[0], start, end, path, NOTE_BEGINS[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)
######

def renyi_entropy(boring_a, alpha):
    """Compute the Renyi entropy for the given model."""
    
    entropy = 0.0
    
    if len(boring_a.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        entropy += pow(boring_a.term_weights[term], alpha)
    
    entropy = log(entropy, 2)
    
    return (1.0 / (1.0 - alpha)) * entropy

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
    boringmatrix.fix_boringmatrix_dicts(results)

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

    # compute the basic entropy of each model.
    # this computes the entropy for the model within the windows, which
    # is the maximum timeframe at this point.  I need to check and make sure
    # we don't have an incorrect last segment.
    entropies = {NOTE_BEGINS[0] : {}, NOTE_BEGINS[1] : {}}

    for start in results[NOTE_BEGINS[0]]:
        entropies[NOTE_BEGINS[0]][start] = boringmatrix.basic_entropy(results[NOTE_BEGINS[0]][start])
        entropies[NOTE_BEGINS[1]][start] = boringmatrix.basic_entropy(results[NOTE_BEGINS[1]][start])

    output_basic_entropy(entropies, "%s_entropy.eps" % output_name)
    output_inverse_entropy(entropies, "%s_inv_entropy.eps" % output_name)
    output_top_model_entropy(results, entropies, "%s_top_models.json" % output_name)

    for alpha in (0.10, 0.25, 0.5, 0.75):
        renyi = {NOTE_BEGINS[0] : {}, NOTE_BEGINS[1] : {}}

        for start in results[NOTE_BEGINS[0]]:
            renyi[NOTE_BEGINS[0]][start] = renyi_entropy(results[NOTE_BEGINS[0]][start], alpha)
            renyi[NOTE_BEGINS[1]][start] = renyi_entropy(results[NOTE_BEGINS[1]][start], alpha)
        output_basic_entropy(renyi, "%s_renyi-%f.eps" % (output_name, alpha))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    