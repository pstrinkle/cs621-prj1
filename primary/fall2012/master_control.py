#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2012
#

import os
import sys
import random
import sqlite3
import subprocess
from json import dumps, loads

from datetime import timedelta

import boringmatrix

NOTE_BEGINS = ("i495", "boston")
TOP_TERM_CNT = 1000

def output_similarity_gnuplot(vector, output):
    """vector here is a dictionary keyed on the datetimestamp as long, with the
    value as the cosine (or other) similarity."""

    skey = sorted(vector.keys())
    start = skey[0]
    end = skey[-1]

    out = []
    random.seed()
    
    path = "%d.%d" % (random.getrandbits(random.randint(16, 57)),
                      random.getrandbits(random.randint(16, 57)))

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
    
    os.remove(path)

def non_zero_count(list_of_counts):
    """Returns the number of non-zero entries, this is similar to the matlab
    method."""

    return len([value for value in list_of_counts if value > 0])

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
    for note in NOTE_BEGINS:
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
            for note in NOTE_BEGINS:
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

    print "usage: %s -in <model_data> -out <output_file> [-short]" % sys.argv[0]
    print "usage: %s -out <output_file> -db <sqlite_db> [-sw <stopwords.in>] [-si <singletons.in>] -i <interval in seconds> [-step]" % sys.argv[0]

    print "-short - terms that appear more than once in at least one slice are used for any other things you output."

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
            elif "-short" == sys.argv[idx]:
                use_short_terms = True
            elif "-step" == sys.argv[idx]:
                step_intervals = True
    except IndexError:
        usage()
        sys.exit(-2)

    if len(NOTE_BEGINS) != 2:
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

        print len(term_list)
        print len(sterm_list)

        # ----------------------------------------------------------------------
        # Compute the size of the set of values greater than one in occurrence
        # per model instance.
        #greater_counts = {NOTE_BEGINS[0] : [], NOTE_BEGINS[1] : []}
        #for start in results[NOTE_BEGINS[0]]:
        #    greater_counts[NOTE_BEGINS[0]].append(results[NOTE_BEGINS[0]][start].greater_than_one())
        #    greater_counts[NOTE_BEGINS[1]].append(results[NOTE_BEGINS[1]][start].greater_than_one())

        #print greater_counts[NOTE_BEGINS[0]]
        #print greater_counts[NOTE_BEGINS[1]]

        # ----------------------------------------------------------------------
        # Prune out low term counts; re-compute.
        if use_short_terms:
            for note in results:
                for start in results[note]:
                    results[note][start].drop_not_in(sterm_list)
                    results[note][start].compute()

        # ----------------------------------------------------------------------
        # Compute the cosine similarities. 
        # YOU NEED TO CALL .compute() before this or you'll get garbage.
        vector_sums = boringmatrix.get_vectorsums(results, NOTE_BEGINS)
        
        # ----------------------------------------------------------------------
        # Compute the similarity and counts for the given models as well as the
        # entropy.
        for start in results[NOTE_BEGINS[0]]:
            # These are identical... as they should be.  Really, I should be using these.
            # Totally different than those above.
            count_cosine[int(start)] = \
                boringmatrix.boring_count_similarity(results[NOTE_BEGINS[0]][start],
                                                     results[NOTE_BEGINS[1]][start])

            weight_cosine[int(start)] = \
                boringmatrix.boring_weight_similarity(results[NOTE_BEGINS[0]][start],
                                                      results[NOTE_BEGINS[1]][start])
            
        # Consider using a few panes.
        output_similarity_gnuplot(vector_sums, "%s_%s.eps" % (output_name, "sims"))
        output_similarity_gnuplot(count_cosine, "%s_%s.eps" % (output_name, "sims_count"))
        output_similarity_gnuplot(weight_cosine, "%s_%s.eps" % (output_name, "sims_weight"))

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
