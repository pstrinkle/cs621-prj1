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

import os
import sys
import time
import sqlite3
import operator
import threading
import multiprocessing

sys.path.append(os.path.join("..", "tweetlib"))
import TweetClean

sys.path.append(os.path.join("..", "modellib"))
import VectorSpace
import Centroid

def usage():
  print "usage: %s <sqlite_db> <minimum> <maximum> <stopwords> <output_folder>" \
    % sys.argv[0]

def buildDocTfIdf(users_tweets, stopwords):

  totalTermCount = 0 # total count of all terms
  docFreq = {}       # dictionary of in how many documents the "word" appears
  invdocFreq = {}    # dictionary of the inverse document frequencies
  docTermFreq = {}   # dictionary of term frequencies by date as integer
  docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values

  for id in users_tweets:

    if users_tweets[id] == None:
      continue

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

    totalTermCount += len(pruned)

    for w in pruned:
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

  # Calculate the inverse document frequencies.
  invdocFreq = VectorSpace.calculate_invdf(len(docTermFreq), docFreq)

  # Calculate the tf-idf values.
  docTfIdf = VectorSpace.calculate_tfidf(
                                         totalTermCount,
                                         docTermFreq,
                                         invdocFreq)

  return docTfIdf

def findMatrixMax(matrix):
  """
  This provides the outer and inner key and the value, of the maximum value.
  """

  max_val = 0.0
  max_i = 0
  max_j = 0

  for i in matrix.keys():

    # sys.stderr.write("why are there no things for %d\n" % i)
    #if len(matrix[i]) == 0: ## checking each time is slow.
      #continue

    # this should be faster than searching by key on the inner loop.
    #
    # Double-looping keys and checking each took:                     4.50s.
    # Single-looping keys and building sorted list in 3 steps took: 122.00s.
    # " performing custom sort (w/ iteritems()):                      9.33s.
    # " (w/ items()):                                                58.33s.
    # Single-looping keys and max() operator instead of sort:         2.35s
    # " (w/o the length check):                                       2.22s

    try:
      kvp = max(matrix[i].iteritems(), key=operator.itemgetter(1))
    except ValueError: # if matrix[i] is None, then this moves forward
      continue         # The way I'm doing this, it doesn't have to check each time.

    # is iteritems() faster?

    #print "%s" % str(kvp)
    #sys.exit(-1)

    #print "max v: %s" % str(sorted_tokens[0][0])
    #print "key: %s" % str(sorted_tokens[0][1])
    
    # Maybe I should store the max value with the array, and then always store
    # the previous largest, and when i insert or delete...
    
    if kvp[1] > max_val:
      max_val = kvp[1]
      max_i = i
      max_j = kvp[0]

  return (max_i, max_j, max_val)

def removeMatrixEntry(matrix, key):
  """
  This removes any matrix key entries, outer and inner.
  """

  try:
    del matrix[key]
  except KeyError:
    print "deleting matrix[%s]" % str(key)
    print "%s" % matrix.keys()
    raise Exception

  for i in matrix.keys():
    try:
      del matrix[i][key]
    except KeyError:
      continue

def addMatrixEntry(matrix, centroids, new_centroid, name):
  """
  Add this entry and comparisons to the matrix, the key to use is name.
  
  Really just need to matrix[name] = {}, then for i in matrix.keys() where not
  name, compare and add.
  
  Please remove before you add, otherwise there can be noise in the data.
  """

  if name in matrix:
    print "enabling matrix[%s] <-- already there!" % str(name)

  matrix[name] = {}

  for i in matrix.keys():
    if i != name:
      matrix[name][i] = Centroid.similarity(centroids[i], new_centroid)

def threadMain(database_file, output_folder, users, stopwords, start, cnt):
  
  query_tweets = "select id, contents as text from tweets where owner = %d;"
  users_tweets = {}

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()

  # -------------------------------------------------------------------------
  # Process this thread's users.
  for u in xrange(start, start + cnt):
    user_id = users[u]
  
    docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values
    users_tweets = {}
    output = "%d\t%d\t%.3f\t%.3f\t%d\t%fm"
    
    start = time.clock()
    
    for row in c.execute(query_tweets % user_id):
      if row['text'] is not None: # I really don't care about tweets I don't have.
        users_tweets[row['id']] = row['text']

    curr_cnt = len(users_tweets)

    docTfIdf = buildDocTfIdf(users_tweets, stopwords)

    # -------------------------------------------------------------------------
    # Build Centroid List (this step is not actually slow.)
    centroids = {}
    arbitrary_name = 0

    for doc, vec in docTfIdf.iteritems():
      centroids[arbitrary_name] = Centroid.Centroid(str(doc), vec) 
      arbitrary_name += 1

    # The size of sim_matrix is: (num_centroids^2 / 2) - (num_centroids / 2)
    # -- verified, my code does this correctly. : )

    sim_matrix = Centroid.getSimMatrix(centroids)
    initial_similarities = Centroid.getSimsFromMatrix(sim_matrix)
    average_sim = Centroid.findAvg(centroids, True, initial_similarities)
    stddev_sim = Centroid.findStd(centroids, True, initial_similarities)

    # Merge centroids by highest similarity of at least threshold  
    threshold = stddev_sim

    # -------------------------------------------------------------------------
    # Merge centroids
    while len(centroids) > 1:
      i, j, sim = findMatrixMax(sim_matrix)

      if sim >= threshold:
        
        centroids[i].addCentroid(centroids[j])
        del centroids[j]

        removeMatrixEntry(sim_matrix, i)
        removeMatrixEntry(sim_matrix, j)
        addMatrixEntry(sim_matrix, centroids, centroids[i], i)
      else:
        break

    duration = (time.clock() - start) / 60 # for minutes

    print output % \
      (user_id, curr_cnt, average_sim, stddev_sim, len(centroids), duration)

    with open(os.path.join(output_folder, "%d.topics" % user_id), "w") as f:
      f.write("user: %d\n#topics: %d\n" % (user_id, len(centroids)))
      # Might be better if I just implement __str__ for Centroids.
      for cen in centroids:
        f.write("%s\n" % centroids[cen].topTerms(10))
      f.write("------------------------------------------------------------\n")

  conn.close()

def main():

  # Did they provide the correct args?
  if len(sys.argv) != 6:
    usage()
    sys.exit(-1)

  cpus = multiprocessing.cpu_count()

  # ---------------------------------------------------------------------------
  # Parse the parameters.
  database_file = sys.argv[1]
  minimum = int(sys.argv[2])
  maximum = int(sys.argv[3])
  stop_file = sys.argv[4]
  output_folder = sys.argv[5]
  
  if minimum >= maximum:
    usage()
    sys.exit(-2)

  # Pull stop words
  stopwords = TweetClean.importStopWords(stop_file)

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

  print kickoff % (database_file, minimum, maximum, output_folder, stop_file) 

  # this won't return the 3 columns we care about.
  query_collect = \
    "select owner from tweets group by owner having count(*) >= %d and count(*) < %d;"
  query_tweets = "select id, contents as text from tweets where owner = %d;"

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()

  # ---------------------------------------------------------------------------
  # Search the database file for users.
  users = []

  start = time.clock()

  for row in c.execute(query_collect % (minimum, maximum)):
    users.append(row['owner'])

  print "query time: %f" % (time.clock() - start)
  print "users: %d\n" % len(users)

  conn.close()

  # ---------------------------------------------------------------------------
  # Process those tweets by user set.

  print "usr\tcnt\tavg\tstd\tend\tdur"
  
  cnt = int(math.ceil((float(len(users)) / cpus)))
  remains = len(users)
  threads = []

  for i in range(0, cpus):
    start = i * cnt

    if cnt > remains:
      cnt = remains

    t = threading.Thread(
                         target=threadMain,
                         args=(
                               database_file,
                               output_folder,
                               users,
                               stopwords,
                               start,
                               cnt,))
    threads.append(t)
    t.start()

    remains -= cnt

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()

