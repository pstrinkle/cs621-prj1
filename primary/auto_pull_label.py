#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This script is meant to encompass: tweets_by_user, pull_from_database, and
# cluster_words.
#
# This will find the users from the specified database with at least X tweets
# in the database.  It will then pull those tweets one user at a time and then
# attempts to clean them up and categorize them by clustering by their tf-idf
# similarities and choosing the highest scored terms as the category label.
#
# The tweet centroids are merged if their similarity score is greater than the
# standard deviation of all similarities in the user's set.

import sys
import sqlite3

sys.path.append("tweetlib")
import TweetClean

sys.path.append("modellib")
import VectorSpace
import Centroid

def usage():
  print "usage: %s <sqlite_db> <minimum> <stopwords> <output>" % sys.argv[0]

def main():

  # Did they provide the correct args?
  if len(sys.argv) != 5:
    usage()
    sys.exit(-1)

  # ---------------------------------------------------------------------------
  # Parse the parameters.
  database_file = sys.argv[1]
  minimum = int(sys.argv[2])
  stop_file = sys.argv[3]
  output_file = sys.argv[4]
  
  # Pull stop words
  with open(stop_file, "r") as f:
    stopwords = f.readlines()

  # clean them up!
  for i in xrange(0, len(stopwords)):
    stopwords[i] = stopwords[i].strip()

  print "database: %s\nminimum: %d\noutput: %s\nstop: %s" % (database_file, minimum, output_file, stop_file) 

  # this won't return the 3 columns we care about.
  query_collect = "select owner from tweets group by owner having count(*) >= %d;"
  query_tweets = "select id, contents as text from tweets where owner = %d;"

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()

  # ---------------------------------------------------------------------------
  # Search the database file for users.
  users = []

  for row in c.execute(query_collect % minimum):
    users.append(row['owner'])

  print "users: %d" % len(users)

  # ---------------------------------------------------------------------------
  # Process those tweets by user set.

  tweet_cnt = 0

  print "user\tcnt"

  for u in users:
    
    # These variables are per user, because users aren't clustered with each 
    # other here.
    
    totalTermCount = 0 # total count of all terms
    docFreq = {}       # dictionary of in how many documents the "word" appears
    invdocFreq = {}    # dictionary of the inverse document frequencies
    docTermFreq = {}   # dictionary of term frequencies by date as integer
    docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values
    
    # could easily just have the thing not store them early.
    # this way though, we don't collect all the tweets for all the users
    # beforehand and store them in memory.
    users_tweets = {}
    for row in c.execute(query_tweets % u):
      users_tweets[row['id']] = row['text']
      tweet_cnt += 1
    
    print "%d\t%d" % (u, len(users_tweets)),
    
    progress = 0.0
    processed = 0
    
    for id in users_tweets:
      users_tweets[id] = TweetClean.cleanup(users_tweets[id], True, True)
      
      # Calculate Term Frequencies for this id/document.
      # Skip 1 letter words.
      words = users_tweets[id].split(' ')

      # let's make a short list of the words we'll accept.
      pruned = []

      for w in words:
        if len(w) > 1 and w not in stopwords:
          pruned.append(w)

      if len(pruned) < 2:
        continue

      docTermFreq[id] = {} # Prepare the dictionary for that document.

      for w in pruned:
        totalTermCount += 1

        try:
          docTermFreq[id][w] += 1
        except KeyError:
          docTermFreq[id][w] = 1

      # Contribute to the document frequencies.
      for w in docTermFreq[id]:
        try:
          docFreq[w] += 1
        except KeyError:
          docFreq[w] = 1
      
      #print ".",

    print "" # for newline

    # Calculate the inverse document frequencies.
    invdocFreq = VectorSpace.calculate_invdf(len(docTermFreq), docFreq)

    # Calculate the tf-idf values.
    docTfIdf = VectorSpace.calculate_tfidf(totalTermCount, docTermFreq, invdocFreq)

    # Build Centroid List
    # XXX: This step is slow.  They should be centroids from the get-go; so I'm
    # going to need to copy some of the VectorSpace (or re-use) code into the
    # centroid thing.
    centroids = {}
    arbitrary_name = 0

    for doc, vec in docTfIdf.iteritems():
      centroids[arbitrary_name] = Centroid.Centroid(str(doc), vec) 
      arbitrary_name += 1

    # Significant speedup, since now I only build the list once per user at this
    #  step, instead of twice.
    initial_similarities = Centroid.getSims(centroids)
    average_sim = Centroid.findAvg(centroids, True, initial_similarities)
    stddev_sim = Centroid.findStd(centroids, True, initial_similarities)

    # Merge centroids by highest similarity of at least threshold  
    threshold = stddev_sim

    while len(centroids) > 1:
      print " %d" % len(centroids)
      # This findMax is slow, because I should cache the values -- like my c#
      # program.  Some similarity values are no longer valid, and now a new loop
      #  needs to be performed. -- Except here, we're not doing it by name, 
      # they're in a list -- not a dictionary.  So if we change to a dictionary
      # we'll need to either give them meaningless names -- like sequentially
      # numbered ... that might be better.  Then I can just recompute on 
      # addition.
      i, j, sim = Centroid.findMax(centroids)

      if sim >= threshold:
        centroids[i].addVector(centroids[j].name, centroids[j].vectorCnt, centroids[j].centroidVector)
        del centroids[j]
      else:
        break

    with open(output_file, "a") as f:
      f.write("user: %d\n" % u)
      for cen in centroids:
        f.write("%s\n" % Centroid.topTerms(cen, 10))
      f.write("-------------------------------------------------------------\n")

  # ---------------------------------------------------------------------------
  # Done.
  conn.close()
  
  print "tweet count: %d" % tweet_cnt

if __name__ == "__main__":
  main()

