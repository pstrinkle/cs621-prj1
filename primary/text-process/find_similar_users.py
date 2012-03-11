#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This program builds a tf-idf matrix.
#

import os
import sys
import sqlite3
import operator

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean

sys.path.append(os.path.join("..", "modellib"))
import vectorspace
import centroid

def top_terms(vector, num):
    """
    Returns the num-highest tf-idf terms in the vector.
    
    This returns the array of terms, not the values.
    
    num := the number of terms to get.
    """

    # This doesn't seem to work right when I used it here.  It works fine
    # in manual python testing and in the centroid library (i'm assuming).
    sorted_tokens = sorted(
                           vector.items(),
                           key=operator.itemgetter(1), # (1) is value
                           reverse=True)

    # count to index
    terms = []
  
    for i in xrange(0, min(num, len(sorted_tokens))):
        terms.append(sorted_tokens[i][0])

    return terms

def data_pull(database_file, query):
    """Pull the data from the database."""
    
    user_tweets = {}
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    
    for row in conn.cursor().execute(query):
        if row['text'] is not None:
            data = tweetclean.cleanup(row['text'], True, True)
            try:
                user_tweets[row['owner']].append(data)
            except KeyError:
                user_tweets[row['owner']] = []
                user_tweets[row['owner']].append(data)

    conn.close()

    return user_tweets

def usage():
    """Standard usage message."""
    print "%s <database_file> <minimum> <maximum> <stop_file> <output>" % \
        sys.argv[0]

def main():
    """Main."""

    if len(sys.argv) != 6:
        usage()
        sys.exit(-1)

    # -------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    minimum = int(sys.argv[2])
    maximum = int(sys.argv[3])
    stop_file = sys.argv[4]
    output_file = sys.argv[5]

    if minimum >= maximum:
        print "minimum is larger than maximum"
        usage()
        sys.exit(-2)

    # Pull stop words
    stopwords = tweetclean.import_stopwords(stop_file)

    kickoff = \
"""
-------------------------------------------------------------------
parameters  :
  database  : %s
  minimum   : %d
  maximum   : %d
  output    : %s
  stop      : %s
-------------------------------------------------------------------
"""

    print kickoff % (database_file, minimum, maximum, output_file, stop_file) 

    # this won't return the 3 columns we care about.
    query_collect = "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
    query_prefetch = "select owner, id, contents as text from tweets where owner in (%s);"

    query = query_prefetch % query_collect

    user_tweets = data_pull(database_file, query % (minimum, maximum))

    print "data pulled"
    print "user count: %d" % len(user_tweets)

    # -------------------------------------------------------------------------
    # Convert to a documents into one document per user.

    docperuser = {} # array representing all the tweets for each user.

    for user_id in user_tweets:
        docperuser[user_id] = "".join(user_tweets[user_id])

    if len(docperuser) == 1:
        sys.stderr.write("Insufficient data for tf-idf, only 1 document\n")
        sys.exit(-3)

    tfidf, dictionary = vectorspace.build_doc_tfIdf(docperuser, stopwords, True)
    
    # ---------------------------------------------------------------------------
    # Build Centroid List
    centroids = []

    for doc, vec in tfidf.iteritems():
        centroids.append(centroid.Centroid(str(doc), vec))

    average_sim = centroid.findAvg(centroids)
    stddev_sim = centroid.findStd(centroids)
    
    print "mean: %.10f\tstd: %.10f" % (average_sim, stddev_sim)
    
    # ---------------------------------------------------------------------------
    # Merge centroids by highest similarity of at least threshold  
    threshold = stddev_sim

    while len(centroids) > 1:
        i, j, sim = centroid.findMax(centroids)

        # @warning: This is fairly crap.
        if sim >= threshold:
            centroids[i].addVector(centroids[j].name, centroids[j].vectorCnt, centroids[j].centroidVector)
            del centroids[j]
            print "merged with sim: %.10f" % sim
        else:
            break

    print "len(centroids): %d" % len(centroids)
    print "avg(centroids): %.10f" % average_sim
    print "std(centroids): %.10f" % stddev_sim
    
    for cen in centroids:
        print centroid.topTerms(cen, 10)

    sys.exit(0)

    # Maybe I should determine the top tf-idf values per document and then make
    # that my dictionary of terms. =)
    #
    # Originally, I intended to use clustering to get topics, but really those
    # are just high tf-idf terms that are common among certain documents...

    top_dict = set()

    for doc_id in tfidf:
        terms = top_terms(tfidf[doc_id], 250)
        #print "terms of %d: %s" % (doc_id, terms)
        for term in terms:
            top_dict.add(term)

    print "total top terms (not the set): %d" % (250 * len(tfidf))
    print "top dict: %d" % len(top_dict)

    # Dump the matrix.
    with open(output_file, "w") as fout:
        #fout.write(vectorspace.dump_raw_matrix(dictionary, tfidf) + "\n")
        fout.write(vectorspace.dump_raw_matrix(top_dict, tfidf) + "\n")

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
