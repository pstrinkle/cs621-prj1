#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#
# This outputs the input model for global processing.

import os
import sys
import random
import subprocess
from json import dumps, loads

import boringmatrix

sys.path.append("../modellib")
import vectorspace

NOTE_BEGINS = ("i495", "boston")

def output_full_matrix(terms, vectors, output):
    """Output the vectors over the terms, this is for each t for a specific 
    location."""

    x = boringmatrix.dump_weights_matrix(terms, vectors)

    with open(output, 'w') as fout:
        fout.write(x)

def build_gtermlist(global_views):
    """Given the thing for globals, go through and build list."""

    terms = {}
    for start in global_views:
        for term in global_views[start].term_matrix:
            try:
                terms[term] += 1
            except KeyError:
                terms[term] = 1
    
    return sorted(terms.keys())

def output_distinct_graphs(results, output, use_file_out = False):
    """Prints a series of distinct term counts for each time interval."""

    title = "Number of Distinct Terms in Top-Level Hierarchical per Interval"
    skey = sorted(results.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %d" % (idx, len(results[skey[idx]].term_matrix)))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'distinct terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, 'global', start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)
    

def output_global_new_terms(results, output, use_file_out = False):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    title = "New Terms in Top-Level Hierarchical Model per Interval"
    skey = sorted(results.keys())
    start = skey[0]
    end = skey[-1]

    aterms = {}

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        count1 = 0

        list1 = results[skey[idx]].term_matrix

        for term in list1:
            if term not in aterms:
                aterms[term] = 1
                count1 += 1

        out.append("%d %d" % (idx, count1))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'new distinct terms'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, 'global', start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_global_entropy(entropies, output, use_file_out = False):
    """Output the basic global entropy chart."""

    title = "Entropy of Top-Level Hierarch per Interval"
    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        out.append("%d %f" % (idx, entropies[skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def output_global_inverse_entropy_json(global_models, entropies, output, x):
    """Output the top values of the global bit, when inverse entropy is above X."""

    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]
    
    output_model = {}
    
    for key in skey:
        val = entropies[key]
        if val > 0.0:
            inv = 1.0 - val
            if inv > x:
                print "%d - %f" % (key, inv)
                print "%d - %d" % (key, global_models[key].total_count)

        output_model[skey[idx]] = vectorspace.top_terms(global_models[key].term_weights, 10)

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))

def output_global_inverse_entropy(entropies, output, use_file_out = False):
    """Output the basic global entropy chart."""

    title = "1-Entropy of Top-Level Hierarch per Interval"
    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

    for idx in range(0, len(skey)):
        val = entropies[skey[idx]]
        if val > 0.0:
            out.append("%d %f" % (idx, 1.0 - val))
        else:
            out.append("%d %f" % (idx, 0.0))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    if use_file_out:
        with open("%s.data" % output, 'w') as fout:
            fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s.eps'\n" % output
    params += "set title '%s'\n" % title
    params += "set xlabel 't'\n"
    params += "set ylabel '(1 - entropy) (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)
    
    os.remove(path)

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short] [-file] [-json]" % sys.argv[0]
    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-file - output as a data file instead of running gnuplot."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5 or len(sys.argv) > 8:
        usage()
        sys.exit(-1)

    use_short_terms = False
    use_file_out = False
    output_json = False
    output_matrix = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-file" == sys.argv[idx]:
                use_file_out = True
            elif "-json" == sys.argv[idx]:
                output_json = True
            elif "-matrix" == sys.argv[idx]:
                output_matrix = True
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

    # ----------------------------------------------------------------------
    # Compute the entropy value for the global hierarchical model given the
    # two input models.
    global_views = {}
    entropies = {}

    # Hierarchical model builder.
    for start in results[NOTE_BEGINS[0]]:
        global_views[start] = \
            boringmatrix.HierarchBoring(results[NOTE_BEGINS[0]][start],
                                        results[NOTE_BEGINS[1]][start])

        global_views[start].compute()
        entropies[start] = boringmatrix.basic_entropy(global_views[start])

    gterm_list = build_gtermlist(global_views)

    output_distinct_graphs(global_views, "%s_%s" % (output_name, "global_distinct"), use_file_out)
    output_global_new_terms(global_views, "%s_%s" % (output_name, "global_newterms"), use_file_out)

    output_global_entropy(entropies, "%s_global_entropy" % output_name, use_file_out)
    output_global_inverse_entropy(entropies, "%s_inv_global_entropy" % output_name, use_file_out)

    if output_matrix:
        output_full_matrix(gterm_list, global_views, "%s_%s.csv" % (output_name, "global"))

    if output_json:
        output_global_inverse_entropy_json(global_views, entropies, "%s.json" % output_name, 0.25)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
    