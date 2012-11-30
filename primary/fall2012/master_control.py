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
from math import log10
import subprocess

import boringmatrix

sys.path.append("../modellib")
import vectorspace

note_begins = ("i495", "boston")

def output_distinct_graphs(vector, graph_title, output):
    """Prints a series of distinct term counts for each time interval.
    
    The vector is as such: vector[timestart]."""
    
    skey = sorted(vector.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"
    for idx in range(0, len(skey)):
        boring = vector[skey[idx]]
        out.append("%d %d" % (idx, len(boring.term_matrix)))
    with open(path, 'w') as fout:
        fout.write("\n".join(out))

    params = "set terminal postscript\n"
    params += "set output '%s'\n" % output
    #params += "set log xy\n"
    params += "set xlabel 't'\n"
    params += "set ylabel 'distinct terms'\n"
    params += "plot '%s' t '%s: %d - %d'\n" % (path, graph_title, start, end)
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

def output_basic_entropy(entropies, output):
    """Output the basic entropy chart."""

    skey = sorted(entropies[note_begins[0]].keys())
    start = skey[0]
    end = skey[-1]

    out = []
    path = "local.tmp.data"
    for idx in range(0, len(skey)):
        out.append("%d %f %f" % (idx, entropies[note_begins[0]][skey[idx]], entropies[note_begins[1]][skey[idx]]))
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

def basic_entropy(boring_a):
    """Compute the H(P) for the given model."""
    
    entropy = 0.0
    for term in boring_a.term_matrix:
        entropy += (boring_a.term_weights[term] * log10(1.0/boring_a.term_weights[term]))
    
    return entropy

def cooccurrence_terms(boring_a, boring_b):
    """Return a list of terms that appear in both model instances."""

    coterms = []

    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            coterms.append(term)

    return coterms

def cooccurrence_weights(boring_a, boring_b):
    """Return a list of terms and their perspective weights between both model
    instances."""
    
    coterms = {}
    
    for term in boring_a.term_matrix:
        if term in boring_b.term_matrix:
            coterms[term] = float(boring_a.term_matrix[term] + boring_b.term_matrix[term]) / (boring_a.total_count + boring_b.total_count)
    
    return coterms

def build_basic_model(stopwords_file, singletons_file, database_file, interval, output_name):
    """Build the output model."""

    remove_em = []

    with open(stopwords_file, 'r') as fin:
        remove_em.extend(loads(fin.read()))

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
            currtime += delta
            end = boringmatrix.long_from_datetime(currtime)

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
    """."""

    print "usage: %s -in <model_data> [-out <output_file>] [-gh <graph>] [-en <basic>]" % sys.argv[0]
    print "usage: %s -out <output_file> -db <sqlite_db> -sw <stopwords.in> -si <singletons.in> -i <interval in seconds>" % sys.argv[0]

    # XXX: I would use pickle, but these are human-readable.
    print "\tmodel_data := don't build the model, this is a dictionary of BoringMatrix instances"
    print "\tsqlite_db := the input database."
    print "\tstopwords.in := json dump of a stop word array."
    print "\tsingletons.in := json dump of a single word array."
    print "\toutput_file := currently just dumps whatever the current meaning of results is."
    print "\tinterval in seconds := is the time slicing to use."
    print "\t-en := 'basic' or ... this outputs the basic entropy for each note for each t."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) < 5:
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
    graph_out = None

    # could use the stdargs parser, but that is meh.
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
            graph_out = sys.argv[idx + 1]
        elif "-en" == sys.argv[idx]:
            entropy_out = sys.argv[idx + 1]

    if len(note_begins) != 2:
        sys.stderr.write("use this to compare two sets.\n")
        sys.exit(-1)

    if build_model:
        build_basic_model(stopwords_file, singletons_file, database_file, interval, output_name)
    else: # not building the model.
        neato_out = []
        vector_sums = {}
        results = None

        if model_file is None:
            sys.exit(-1)

        with open(model_file, 'r') as moin:
            results = loads(moin.read(), object_hook=boringmatrix.as_boring)
            # dict(loads(moin.read(), object_hook=as_boring))

        # compute the term weights.
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

        # compute the cosine similarities.
        for start in results[note_begins[0]]:
            vector_sums[int(start)] = \
                vectorspace.cosine_compute(results[note_begins[0]][start].term_weights,
                                           results[note_begins[1]][start].term_weights)

        if graph_out is not None:
            output_similarity_gnuplot(vector_sums, "%s_%s.eps" % (graph_out, "sims"))
            output_distinct_graphs(results[note_begins[0]], note_begins[0], "%s_%s.eps" % (graph_out, note_begins[0]))
            output_distinct_graphs(results[note_begins[1]], note_begins[1], "%s_%s.eps" % (graph_out, note_begins[1]))

            # compute the basic entropy of each model.
            # this computes the entropy for the model within the windows, which
            # is the maximum timeframe at this point.  I need to check and make sure
            # we don't have an incorrect last segment.
            if entropy_out is not None:
                entropies = {note_begins[0] : {}, note_begins[1] : {}}
                for start in results[note_begins[0]]:
                    entropies[note_begins[0]][start] = basic_entropy(results[note_begins[0]][start])
                    entropies[note_begins[1]][start] = basic_entropy(results[note_begins[1]][start])
                output_basic_entropy(entropies, "%s_entropy.eps" % graph_out)

        if output_name is not None:
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
