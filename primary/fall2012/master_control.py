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
from math import log10, log
import subprocess

import boringmatrix

sys.path.append("../modellib")
import vectorspace

note_begins = ("i495", "boston")
TOP_TERM_CNT = 1000

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
            output_model[skey[idx]] = (vectorspace.top_terms(results[note_begins[0]][skey[idx]].term_weights, 10),
                                       vectorspace.top_terms(results[note_begins[1]][skey[idx]].term_weights, 10))

    with open(output, 'w') as fout:
        fout.write(dumps(output_model, indent=4))

def basic_dict_entropy(dictionary):
    """Given a P(x) dictionary, return H(P)."""

    entropy = 0.0
    for entry in dictionary:
        entropy += (dictionary[entry] * log10(1.0/dictionary[entry]))

    return entropy

def renyi_entropy(boring_a, alpha):
    """Compute the Renyi entropy for the given model."""
    
    entropy = 0.0
    
    if len(boring_a.term_matrix) == 0:
        return 0.0
    
    for term in boring_a.term_matrix:
        entropy += pow(boring_a.term_weights[term], alpha)
    
    entropy = log(entropy, 2)
    
    return (1.0 / (1.0 - alpha)) * entropy

def non_zero_count(list_of_counts):
    """Returns the number of non-zero entries, this is similar to the matlab
    method."""

    count = 0
    non_zeros = [value for value in list_of_counts if value > 0]

    for value in non_zeros:
        count += 1

    return count

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

    print "usage: %s -in <model_data> -out <output_file> [-short] [-gh [-en]] [-nt]  [-ftm] [-mtm] [-notes]" % sys.argv[0]
    print "usage: %s -out <output_file> -db <sqlite_db> [-sw <stopwords.in>] [-si <singletons.in>] -i <interval in seconds> [-step]" % sys.argv[0]

    print "-short - terms that appear more than once in at least one slice are used for any other things you output."

    print "-nt - output new_terms_out"
    
    print "-stm - output the matrix using the short list, forces short"
    print "-frm - output full_term_matrix_out"
    print "-mtm - output merged_term_matrix_out, uses stm for output, merges the two locations into one model for each t."

    print "\tmodel_data := don't build the model, this is a dictionary of BoringMatrix instances"
    print "\tsqlite_db := the input database."
    print "\tstopwords.in := json dump of a stop word array."
    print "\tsingletons.in := json dump of a single word array."
    print "\toutput_file := currently just dumps whatever the current meaning of results is."
    print "\tinterval in seconds := is the time slicing to use."
    print "\t-en := 'basic' or ... this outputs the basic entropy for each note for each t."
    print "\t-step := should it do half-step t models -- sliding window."
    
    # Need to consider having the output fall out in sets for varied windows...

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
    entropy_out = False
    new_terms_out = False
    full_term_matrix_out = False
    sfull_term_matrix_out = False
    merged_term_matrix_out = False
    notes_out = False
    step_intervals = False
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

        term_list = boringmatrix.build_termlist(results) # length of this is used to normalize
        sterm_list = boringmatrix.build_termlist2(results) # length of this is used to normalize

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
                boringmatrix.output_full_matrix(term_list,
                                                results[note],
                                                "%s_%s_full.csv" % (output_name, note))

        # ----------------------------------------------------------------------
        # Prune out low term counts; re-compute.
        if use_short_terms:
            for note in results:
                for start in results[note]:
                    results[note][start].drop_not_in(sterm_list)
                    results[note][start].compute()

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
                boringmatrix.output_full_matrix(sterm_list,
                                                merged,
                                                "%s_%s.csv" % (output_name, "merged"))
            else:
                boringmatrix.output_full_matrix(term_list,
                                                merged,
                                                "%s_%s.csv" % (output_name, "merged"))

        # ----------------------------------------------------------------------
        # Output the matrices as CSVs... Hopefully as input to matlab.
        if sfull_term_matrix_out:
            for note in results:
                boringmatrix.output_full_matrix(sterm_list,
                                                results[note],
                                                "%s_%s.csv" % (output_name, note))

        # ----------------------------------------------------------------------
        # Compute the cosine similarities. 
        # YOU NEED TO CALL .compute() before this or you'll get garbage.
        for start in results[note_begins[0]]:
            vector_sums[int(start)] = vectorspace.cosine_compute(results[note_begins[0]][start].term_weights,
                                                                 results[note_begins[1]][start].term_weights)
        # ----------------------------------------------------------------------
        # Compute the similarity and counts for the given models as well as the
        # entropy.
        if graph_out:

            for start in results[note_begins[0]]:
                # These are identical... as they should be.  Really, I should be using these.
                # Totally different than those above.
                count_cosine[int(start)] = boringmatrix.boring_count_similarity(results[note_begins[0]][start],
                                                                                 results[note_begins[1]][start])

                weight_cosine[int(start)] = boringmatrix.boring_weight_similarity(results[note_begins[0]][start],
                                                                                  results[note_begins[1]][start])
            
            # Consider using a few panes.
            output_similarity_gnuplot(vector_sums,
                                      "%s_%s.eps" % (output_name, "sims"))
            output_similarity_gnuplot(count_cosine,
                                      "%s_%s.eps" % (output_name, "sims_count"))
            output_similarity_gnuplot(weight_cosine,
                                      "%s_%s.eps" % (output_name, "sims_weight"))
            output_distinct_graphs(results[note_begins[0]],
                                   results[note_begins[1]],
                                   "%s_distinct.eps" % (output_name))

            # compute the basic entropy of each model.
            # this computes the entropy for the model within the windows, which
            # is the maximum timeframe at this point.  I need to check and make sure
            # we don't have an incorrect last segment.
            if entropy_out:
                entropies = {note_begins[0] : {}, note_begins[1] : {}}

                for start in results[note_begins[0]]:
                    entropies[note_begins[0]][start] = boringmatrix.basic_entropy(results[note_begins[0]][start])
                    entropies[note_begins[1]][start] = boringmatrix.basic_entropy(results[note_begins[1]][start])

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
                sorted_weights = sorted(boringmatrix.cooccurrence_weights(results[note_begins[0]][itempair[0]],
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
