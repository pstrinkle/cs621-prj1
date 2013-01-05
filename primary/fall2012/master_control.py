#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#

import sys
import sqlite3
from json import dumps, loads
from operator import itemgetter
from datetime import timedelta
from math import log10, log, pow
import subprocess
import os

import boringmatrix
import termset

sys.path.append("../modellib")
import vectorspace

note_begins = ("i495", "boston")

def output_new_terms(results, output):
    """At each X, indicate on the Y axis how many new terms were introduced."""

    skey = sorted(results[note_begins[0]].keys())
    start = skey[0]
    end = skey[-1]

    aterms = []
    bterms = []

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        count1 = 0
        count2 = 0

        list1 = results[note_begins[0]][skey[idx]].term_matrix
        list2 = results[note_begins[1]][skey[idx]].term_matrix

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
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, note_begins[0], start, end, path, note_begins[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_distinct_graphs(vectorA, vectorB, output):
    """Prints a series of distinct term counts for each time interval.
    
    The vectorA is as such: vector[timestart]."""
    
    skey = sorted(vectorA.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"
    for idx in range(0, len(skey)):
        boringA = vectorA[skey[idx]]
        boringB = vectorB[skey[idx]]
        out.append("%d %d %d" % (idx, len(boringA.term_matrix), len(boringB.term_matrix)))
    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'distinct terms'\n"
    #params += "plot '%s' t '%s: %d - %d'\n" % (path, graph_title, start, end)
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, note_begins[0], start, end, path, note_begins[1], start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_similarity_gnuplot(vector, output):
    """vector here is a dictionary keyed on the datetimestamp as long, with the
    value as the cosine (or other) similarity."""

    skey = sorted(vector.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"
    for idx in range(0, len(skey)):
        out.append("%d %f" % (idx, vector[skey[idx]]))
    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'similarity scores'\n"
    params += "plot '%s' t '%d - %d'\n" % (path, start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_global_entropy(entropies, output):
    """Output the basic global entropy chart."""

    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        out.append("%d %f" % (idx, entropies[skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_global_inverse_entropy(entropies, output):
    """Output the basic global entropy chart."""

    skey = sorted(entropies.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        val = entropies[skey[idx]]
        if val > 0.0:
            out.append("%d %f" % (idx, 1.0 - val))
        else:
            out.append("%d %f" % (idx, 0.0))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel '(1 - entropy) (nats)'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red'\n" % (path, "global", start, end)
    params += "q\n"

    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_renyi_entropy(alpha, entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[note_begins[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[note_begins[0]][skey[idx]],
                                 entropies[note_begins[1]][skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'renyi scores - %f'\n" % alpha
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, note_begins[0], start, end, path, note_begins[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_basic_entropy(entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[note_begins[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx,
                                 entropies[note_begins[0]][skey[idx]],
                                 entropies[note_begins[1]][skey[idx]]))

    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'entropy scores'\n"
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, note_begins[0], start, end, path, note_begins[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_inverse_entropy(entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[note_begins[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"

    for idx in range(0, len(skey)):
        val1 = entropies[note_begins[0]][skey[idx]]
        val2 = entropies[note_begins[1]][skey[idx]]

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
    params += "plot '%s' using 1:2 t '%s: %d - %d' lc rgb 'red', '%s' using 1:3 t '%s: %d - %d' lc rgb 'blue'\n" % (path, note_begins[0], start, end, path, note_begins[1], start, end)
    params += "q\n"
    
    subprocess.Popen(['gnuplot'], stdin=subprocess.PIPE).communicate(params)

def output_top_model_entropy(results, entropies, output):
    """Go through the entropy values and output the top terms from the models, 
    when the entropy goes low beyond some threshold."""
    
    output_model = {}
    
    # entropies[note_begins[0]][start] = basic_entropy()
    # results[note][start] = boringmatrix.BoringMatrix()
    skey = sorted(entropies[note_begins[0]].keys())

    for idx in range(0, len(skey)):
        val1 = entropies[note_begins[0]][skey[idx]]
        val2 = entropies[note_begins[1]][skey[idx]]

        if val1 > 0.0:
            out1 = 1.0 - val1
        else:
            out1 = 0.0

        if val2 > 0.0:
            out2 = 1.0 - val2
        else:
            out2 = 0.0

        if out1 > 0.05 or out2 > 0.05:
            output_model[skey[idx]] = (top_terms(results[note_begins[0]][skey[idx]]),
                                       top_terms(results[note_begins[1]][skey[idx]]))

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))

def output_full_matrix(terms, vectors, output):
    """Output the vectors over the terms, this is for each t for a specific 
    location."""

    x = boringmatrix.dump_weights_matrix(terms, vectors)

    with open(output, 'w') as fout:
        fout.write(x)

def top_terms(boring_a):
    """Return a list of the top terms."""

    return vectorspace.top_terms(boring_a.term_weights, 10)

def basic_dict_entropy(dictionary):
    """Given a P(x) dictionary, return H(P)."""

    entropy = 0.0
    for entry in dictionary:
        entropy += (dictionary[entry] * log10(1.0/dictionary[entry]))

    return entropy

def basic_entropy(boring_a):
    """Compute the H(P) for the given model."""
    
    term_count = len(boring_a.term_matrix)
    if term_count == 0:
        return 0.0
    
    entropy = 0.0
    # could probably do sum(value for term in terms[value])
    for term in boring_a.term_matrix:
        entropy += (boring_a.term_weights[term] * log10(1.0/boring_a.term_weights[term]))
    
    if entropy == 0.0:
        return 0.0

    return entropy / log10(term_count)

def renyi_entropy(boring_a, alpha):
    """Compute the Renyi entropy for the given model."""
    
    entropy = 0.0
    
    if len(boring_a.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        entropy += pow(boring_a.term_weights[term], alpha)
    
    entropy = log(entropy, 2)
    
    return (1.0 / (1.0 - alpha)) * entropy

def cooccurrence_terms(boring_a, boring_b):
    """Return a list of terms that appear in both model instances."""

    coterms = [term for term in boring_a.term_matrix if term in boring_b.term_matrix]

    return coterms

def cooccurrence_weights(boring_a, boring_b):
    """Return a list of terms and their perspective weights between both model
    instances."""
    
    coterms = {}
    
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            coterms[term] = float(boring_a.term_matrix[term] + boring_b.term_matrix[term]) / (boring_a.total_count + boring_b.total_count)
    
    return coterms

def non_zero_count(list_of_counts):
    """Returns the number of non-zero entries, this is similar to the matlab
    method."""

    count = 0
    non_zeros = [value for value in list_of_counts if value > 0]

    for value in non_zeros:
        count += 1

    return count

def sorted_indices(full_list):
    """Return a list of the sorted indices for full_list."""
    
    return [i[0] for i in sorted(enumerate(full_list), key=lambda x:x[1])]

def build_termlist2(result_dict):
    """Tries to build list but only uses terms that appeared more than once 
    within a model instance.
    
    If a term appeared more than once in any instance of the model it is kept,
    whereas a lot of the code drops all terms that only occur once in an 
    instance and this isn't quite the same list."""

    terms = {}
    for note in result_dict:
        for start in result_dict[note]:
            for term in result_dict[note][start].term_matrix:
                if result_dict[note][start].term_matrix[term] > 1:
                    try:
                        terms[term] += 1
                    except KeyError:
                        terms[term] = 1

    return sorted(terms.keys())

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

def build_termlist(result_dict):
    """Given a results dictionary, go through each "note" within it and each 
    BoringMatrix and pull out the terms and build a dictionary thing.
    
    This returns a list of the terms in sorted order.
    
    If you take all the BoringMatrix data sets and given a dictionary return
    the tuples with the term counts then you should be able to do some 
    permutation entropy stuff.
    
    There may be better ways to do this; like when I build the models ---
    actually build_intervals may already output this stuff."""

    terms = {}
    for note in result_dict:
        for start in result_dict[note]:
            for term in result_dict[note][start].term_matrix:
                try:
                    terms[term] += 1
                except KeyError:
                    terms[term] = 1
    
    return sorted(terms.keys())

def build_basic_model(stopwords_file,
                      singletons_file,
                      database_file,
                      interval,
                      output_name,
                      step_intervals):
    """Build the output model."""

    remove_em = []

    if stopwords_file is not None:
        with open(stopwords_file, 'r') as fin:
            remove_em.extend(loads(fin.read()))

    if singletons_file is not None:
        with open(singletons_file, 'r') as fin:
            remove_em.extend(loads(fin.read()))

    # this won't return the 3 columns we care about.
    # XXX: This doesn't select by note.
    query = "select id, cleaned_text from tweets where note like '%s%%' and (yyyymmddhhmmss >= %d and yyyymmddhhmmss < %d);"

    # --------------------------------------------------------------------------
    # Search the database file for the earliest timestamp and latest.

    early_query = "select min(yyyymmddhhmmss) as early, max(yyyymmddhhmmss) as late from tweets;"
    earliest = 0
    latest = 0

    with sqlite3.connect(database_file) as conn: 
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute(early_query)
        row = curr.fetchone()

        earliest = row['early']
        latest = row['late']

        # the timestamps are YYYYMMDDHHMMSS -- so I need to convert them into 
        # datetime.datetime objects; easy.
        # okay, so they want the timestamps to step forward slowly.
        # can use datetime.timedelta correctly updates the datetime value, which
        # we'll then need to convert back to the timestamp long.

    starttime = boringmatrix.datetime_from_long(earliest)
    endtime = boringmatrix.datetime_from_long(latest)
    currtime = starttime
    delta = timedelta(0, interval)
    halfdelta = timedelta(0, interval / 2)

    # datetime.timedelta(0, 1) (days, seconds)
    # you can just add these to datetime.datetime objects.
    #
    # (endtime - starttime) gives you a datetime.timedelta object.

    print "starttime: %s" % starttime
    print "endtime: %s" % endtime
    
    results = {}
    for note in note_begins:
        results[note] = {}

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    with sqlite3.connect(database_file) as conn:
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        
        while currtime + delta < endtime:
            start = boringmatrix.long_from_datetime(currtime)
            
            ending = currtime + delta # should be full interval
            
            end = boringmatrix.long_from_datetime(ending)
            
            # move starting point forward
            if step_intervals:
                currtime += halfdelta
            else:
                currtime += delta

            print "range: %d %d" % (start, end)

            # build the text for that time-slice into one document, removing
            # the stopwords provided by the user as well as the singleton
            # list, neatly also provided by the user.            
            for note in note_begins:
                local_cluster = []

                for row in curr.execute(query % (note, start, end)):
                    local_cluster.append(boringmatrix.localclean(row['cleaned_text']))

                tmp_local = " ".join(local_cluster) # join into one line
                    # then split and strip out bad words.
                # why join and then split immediately thereafter, :P
                # in creating the BoringMatrix it splits, so why not just feed
                # it an array.
                results[note][start] = boringmatrix.BoringMatrix(" ".join([word for word in tmp_local.split(" ") if word not in remove_em and len(word) > 2]))

    with open(output_name, 'w') as fout:
        # added items, you then cast result afterwards.
        # fout.write(dumps(results.items(), cls=BoringMatrixEncoder, sort_keys=True, indent=4))
        fout.write(dumps(results, cls=boringmatrix.BoringMatrixEncoder, sort_keys=True, indent=4))

def usage():
    """Print the massive usage information."""

    print "usage: %s -in <model_data> -out <output_file> [-short] [-gh [-en]] [-gb] [-pm] [-sr] [-nt]  [-ftm] [-mtm] [-notes] [-pca1] [-pca3]" % sys.argv[0]
    print "usage: %s -out <output_file> -db <sqlite_db> [-sw <stopwords.in>] [-si <singletons.in>] -i <interval in seconds> [-step]" % sys.argv[0]

    print "-short - terms that appear more than once in at least one slice are used for any other things you output."
    print "-sr - output set_resemblance_out"
    print "-nt - output new_terms_out"
    
    print "-stm - output the matrix using the short list, forces short"
    print "-frm - output full_term_matrix_out"
    print "-mtm - output merged_term_matrix_out, uses stm for output, merges the two locations into one model for each t."

    # the PCA C code currently doesn't support floating point.
    print "-pca1 - Output folder of files, one per document for full term set, as term counts"
    print "-short -pca1 is pca1 but using the short list."
    #print "-pca2 - Output folder of files, one per document for full term set, as term weights"

    print "\tmodel_data := don't build the model, this is a dictionary of BoringMatrix instances"
    print "\tsqlite_db := the input database."
    print "\tstopwords.in := json dump of a stop word array."
    print "\tsingletons.in := json dump of a single word array."
    print "\toutput_file := currently just dumps whatever the current meaning of results is."
    print "\tinterval in seconds := is the time slicing to use."
    print "\t-en := 'basic' or ... this outputs the basic entropy for each note for each t."
    print "\t-step := should it do half-step t models -- sliding window."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 3:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.

    model_file = None
    output_name = None
    database_file = None
    stopwords_file = None
    singletons_file = None
    interval = None
    build_model = False
    graph_out = False
    global_out = False
    permutation_out = False
    entropy_out = False
    set_resemblance_out = False
    new_terms_out = False
    full_term_matrix_out = False
    sfull_term_matrix_out = False
    merged_term_matrix_out = False
    notes_out = False
    step_intervals = False
    pca1_out = False
    use_short_terms = False

    # could use the stdargs parser, but that is meh.
    try:
        for idx in range(1, len(sys.argv)):
            if "-in" == sys.argv[idx]:
                model_file = sys.argv[idx + 1]
            elif "-out" == sys.argv[idx]:
                output_name = sys.argv[idx + 1]
            elif "-db" == sys.argv[idx]:
                database_file = sys.argv[idx + 1]
                build_model = True
            elif "-sw" == sys.argv[idx]:
                stopwords_file = sys.argv[idx + 1]
            elif "-si" == sys.argv[idx]:
                singletons_file = sys.argv[idx + 1]
            elif "-i" == sys.argv[idx]:
                interval = int(sys.argv[idx + 1])
            elif "-gh" == sys.argv[idx]:
                graph_out = True
            elif "-en" == sys.argv[idx]:
                entropy_out = True
            elif "-gb" == sys.argv[idx]:
                global_out = True
            elif "-pm" == sys.argv[idx]:
                permutation_out = True
            elif "-sr" == sys.argv[idx]:
                set_resemblance_out = True
            elif "-nt" == sys.argv[idx]:
                new_terms_out = True
            elif "-ftm" == sys.argv[idx]:
                full_term_matrix_out = True
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-stm" == sys.argv[idx]:
                sfull_term_matrix_out = True
                use_short_terms = True
            elif "-mtm" == sys.argv[idx]:
                merged_term_matrix_out = True
            elif "-notes" == sys.argv[idx]:
                notes_out = True
            elif "-step" == sys.argv[idx]:
                step_intervals = True
            elif "-pca1" == sys.argv[idx]:
                pca1_out = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(note_begins) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Do the stuff.

    if build_model:
        build_basic_model(stopwords_file,
                          singletons_file,
                          database_file,
                          interval,
                          output_name,
                          step_intervals)
    else:
        # not building the model.
        neato_out = []
        vector_sums = {}
        count_cosine = {}
        weight_cosine = {}
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
        for note in note_begins:
            # this crap only matters for the key thing.
            keys = results[note].keys()

            for idx in range(0, len(keys)):
                results[note][int(keys[idx])] = results[note][keys[idx]]
                del results[note][keys[idx]]

            for start in results[note]:
                results[note][start].compute()

#        for start in results[note_begins[0]]:
#            for note in note_begins:
#                total = 0.0
#                for term in results[note][start].term_weights:
#                    total += results[note][start].term_weights[term]
#                print total,
# 1.0 is the total weight, yay.

        print "number of slices: %d" % len(results[note_begins[0]])

        term_list = build_termlist(results) # length of this is used to normalize
        sterm_list = build_termlist2(results) # length of this is used to normalize

        print len(term_list)
        print len(sterm_list)

        # ----------------------------------------------------------------------
        # Compute the size of the set of values greater than one in occurrence
        # per model instance.
        #greater_counts = {note_begins[0] : [], note_begins[1] : []}
        #for start in results[note_begins[0]]:
        #    greater_counts[note_begins[0]].append(results[note_begins[0]][start].greater_than_one())
        #    greater_counts[note_begins[1]].append(results[note_begins[1]][start].greater_than_one())

        #print greater_counts[note_begins[0]]
        #print greater_counts[note_begins[1]]
        if new_terms_out:
            output_new_terms(results, "%s_term_growth.eps" % output_name)

        if full_term_matrix_out:
            for note in note_begins:
                output_full_matrix(term_list, results[note], "%s_%s_full.csv" % (output_name, note))

        # ----------------------------------------------------------------------
        # Prune out low term counts; re-compute.
        if use_short_terms:
            for note in note_begins:
                for start in results[note]:
                    results[note][start].drop_not_in(sterm_list)
                    results[note][start].compute()

        # ----------------------------------------------------------------------
        # Output each slice for each area as a new-line broken up term count
        # file.  These values aren't normalized, so they're not terribly useful
        # yet.
        if pca1_out:
            outdir = "%s_%s" % (output_name, "pca1")
            os.mkdir(outdir)
            for note in note_begins:
                for slice in results[note]:
                    filename = "%s-%d" % (note, slice)
                    with open(os.path.join(outdir, filename), 'w') as fout:
                        if use_short_terms:
                            for term in sterm_list:
                                if term in results[note][slice].term_matrix:
                                    value = results[note][slice].term_matrix[term]
                                else:
                                    value = 0
                                fout.write("%d\n" % value)
                        else:
                            for term in term_list:
                                if term in results[note][slice].term_matrix:
                                    value = results[note][slice].term_matrix[term]
                                else:
                                    value = 0
                                fout.write("%d\n" % value)

            if use_short_terms:
                print "params: %d %d" % (len(results[note]) * 2, len(sterm_list))
            else:
                print "params: %d %d" % (len(results[note]) * 2, len(term_list))

        # ----------------------------------------------------------------------
        # Output a CSV with a model built from merging boston and i495 for each
        # t.  Using the short list, or whatever is set.
        if merged_term_matrix_out:
            merged = {}
            for start in results[note_begins[0]]:
                x = boringmatrix.BoringMatrix(None)
                
                for note in note_begins:
                    for term in results[note][start].term_matrix:
                        val = results[note][start].term_matrix[term]
                        try:
                            x.term_matrix[term] += val
                        except KeyError:
                            x.term_matrix[term] = val
                        x.total_count += val

                if use_short_terms:
                    x.drop_not_in(sterm_list)

                x.compute()
                merged[start] = x
            if use_short_terms:
                output_full_matrix(sterm_list, merged, "%s_%s.csv" % (output_name, "merged"))
            else:
                output_full_matrix(term_list, merged, "%s_%s.csv" % (output_name, "merged"))

        # ----------------------------------------------------------------------
        # Output the matrices as CSVs... Hopefully as input to matlab.
        if sfull_term_matrix_out:
            for note in note_begins:
                output_full_matrix(sterm_list, results[note], "%s_%s.csv" % (output_name, note))

        # ----------------------------------------------------------------------
        # Compute the entropy value for the global hierarchical model given the
        # two input models.
        if global_out:
            global_views = {}
            entropies = {}

            # Hierarchical model builder.
            for start in results[note_begins[0]]:
                global_views[start] = boringmatrix.HierarchBoring(results[note_begins[0]][start],
                                                                  results[note_begins[1]][start])
                global_views[start].compute()
                entropies[start] = basic_entropy(global_views[start])

            gterm_list = build_gtermlist(global_views)

            output_global_entropy(entropies, "%s_global_entropy.eps" % output_name)
            output_global_inverse_entropy(entropies, "%s_inv_global_entropy.eps" % output_name)
            output_full_matrix(gterm_list, global_views, "%s_%s.csv" % (output_name, "global"))

        # ----------------------------------------------------------------------
        # Compute the cosine similarities. 
        # YOU NEED TO CALL .compute() before this or you'll get garbage.
        for start in results[note_begins[0]]:
            vector_sums[int(start)] = vectorspace.cosine_compute(results[note_begins[0]][start].term_weights,
                                                                 results[note_begins[1]][start].term_weights)

            # These are identical... as they should be.  Really, I should be using these.
            # Totally different than those above.
            count_cosine[int(start)] =  boringmatrix.boring_count_similarity(results[note_begins[0]][start],
                                                                             results[note_begins[1]][start])

            weight_cosine[int(start)] = boringmatrix.boring_weight_similarity(results[note_begins[0]][start],
                                                                              results[note_begins[1]][start])

        # ----------------------------------------------------------------------
        # Compute the permutation entropy for the window.
        #
        # Use set resemblance to get entropy probability value.
        if permutation_out:
            for note in note_begins:
                sorted_indices_dict = {}
                for start in results[note]:
                    full_list = results[note][start].build_fulllist(term_list)
                    indices = sorted_indices(full_list)
                    try:
                        sorted_indices_dict[str(indices)] += 1
                    except KeyError:
                        sorted_indices_dict[str(indices)] = 1


        # ----------------------------------------------------------------------
        # Convert to sets and compute the set resemblances, see if any are 
        # high, compared to each other at each t.
        if set_resemblance_out:        
            termSets = {}
            for start in results[note_begins[0]]:
                set_a = termset.TermSet(results[note_begins[0]][start], "%s.%s" % (note_begins[0], str(start)))
                set_b = termset.TermSet(results[note_begins[1]][start], "%s.%s" % (note_begins[1], str(start)))

                termSets[start] = termset.set_resemblance(set_a, set_b)

            #print sorted(
            #             termSets.items(),
            #             key=itemgetter(1), # (1) is value
            #             reverse=True)

            # ------------------------------------------------------------------
            # Convert to sets and compute the set resemblances for the goal of 
            # clustering all the sets so that I can build a "table" for each t 
            # in T, the bin ID of Xt, Yt | counts --> so I have probabilities 
            # to build the entropy computation for the window.
            termSetsFull = []
            for note in note_begins:
                for start in results[note]:
                    termSetsFull.append(termset.TermSet(results[note][start], "%s.%s" % (note, str(start))))

            resem_matrix = {}
            length = len(termSetsFull)

            for i in xrange(0, length):
                resem_matrix[i] = {}

                for j in xrange(i + 1, length):
                    resem_matrix[i][j] = termset.set_resemblance(termSetsFull[i],
                                                                 termSetsFull[j])

            resem_values = []
            for i in resem_matrix:
                for j in resem_matrix[i]:
                    resem_values.append(resem_matrix[i][j])

            #print dumps(sorted(resem_values, reverse=True), indent=4)

            resem_histogram = {0.1 : 0,
                               0.2 : 0,
                               0.3 : 0,
                               0.4 : 0,
                               0.5 : 0,
                               0.6 : 0,
                               0.7 : 0,
                               0.8 : 0,
                               0.9 : 0,
                               1.0 : 0}
            for value in resem_values:
                if value <= 0.1:
                    resem_histogram[0.1] += 1
                elif value <= 0.2:
                    resem_histogram[0.2] += 1
                elif value <= 0.3:
                    resem_histogram[0.3] += 1
                elif value <= 0.4:
                    resem_histogram[0.4] += 1
                elif value <= 0.5:
                    resem_histogram[0.5] += 1
                elif value <= 0.6:
                    resem_histogram[0.6] += 1
                elif value <= 0.7:
                    resem_histogram[0.7] += 1
                elif value <= 0.8:
                    resem_histogram[0.8] += 1
                elif value <= 0.9:
                    resem_histogram[0.9] += 1
                else:
                    resem_histogram[1.0] += 1

            print dumps(resem_histogram, indent=4)

            #print sorted(
            #             resem_matrix.items(),
            #             key=itemgetter(1), # (1) is value
            #             reverse=True)


        # ----------------------------------------------------------------------
        # Compute the similarity and counts for the given models as well as the
        # entropy.
        if graph_out:
            # Consider using a few panes.
            output_similarity_gnuplot(vector_sums, "%s_%s.eps" % (output_name, "sims"))
            output_similarity_gnuplot(count_cosine, "%s_%s.eps" % (output_name, "sims_count"))
            output_similarity_gnuplot(weight_cosine, "%s_%s.eps" % (output_name, "sims_weight"))
            output_distinct_graphs(results[note_begins[0]],
                                   results[note_begins[1]],
                                   "%s_distinct.eps" % (output_name))

            # compute the basic entropy of each model.
            # this computes the entropy for the model within the windows, which
            # is the maximum timeframe at this point.  I need to check and make sure
            # we don't have an incorrect last segment.
            if entropy_out:
                entropies = {note_begins[0] : {},
                             note_begins[1] : {}}

                for start in results[note_begins[0]]:
                    entropies[note_begins[0]][start] = basic_entropy(results[note_begins[0]][start])
                    entropies[note_begins[1]][start] = basic_entropy(results[note_begins[1]][start])

                output_basic_entropy(entropies, "%s_entropy.eps" % output_name)
                output_inverse_entropy(entropies, "%s_inv_entropy.eps" % output_name)
                output_top_model_entropy(results, entropies, "%s_top_models.json" % output_name)

                for alpha in (0.10, 0.25, 0.5, 0.75):
                    renyi = {note_begins[0] : {}, note_begins[1] : {}}

                    for start in results[note_begins[0]]:
                        renyi[note_begins[0]][start] = renyi_entropy(results[note_begins[0]][start], alpha)
                        renyi[note_begins[1]][start] = renyi_entropy(results[note_begins[1]][start], alpha)
                    output_basic_entropy(renyi, "%s_renyi-%f.eps" % (output_name, alpha))

        # ----------------------------------------------------------------------
        # 
        if notes_out:
            sorted_sums = sorted(vector_sums.items(),
                                 key=itemgetter(1), # (1) is value
                                 reverse=True)

            for itempair in sorted_sums:
                sorted_weights = sorted(cooccurrence_weights(results[note_begins[0]][itempair[0]],
                                                             results[note_begins[1]][itempair[0]]).items(),
                                        key=itemgetter(1),
                                        reverse=True)

                #wcnt = max(10, int(math.floor(len(sorted_weights) * 0.10)))
                #wcnt = min(10, int(math.floor(len(sorted_weights) * 0.10)))
                wcnt = min(10, len(sorted_weights))

                neato_out.append((str(boringmatrix.datetime_from_long(itempair[0])),
                                  itempair[1],
                                  len(sorted_weights),
                                  sorted_weights[0:wcnt]))

            with open(output_name, 'w') as fout:
                fout.write(dumps(neato_out, indent=4))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
