#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This script is meant to encompass: tweets_by_user, pull_from_database, and
# cluster_words, and auto_lda_gensim.
#
# This will find the users from the specified database with at least X tweets
# in the database.  It will then pull those tweets one user at a time and then
# attempts to clean them up and categorize them by clustering by their tf-idf
# similarities and choosing the highest scored terms as the category label.
#
# The tweet centroids are merged if their similarity score is greater than the
# standard deviation of all similarities in the user's set.
#
# The tf-idf library code here is of my own design.  It is fairly standard, 
# except I don't throw out singletons.  Maybe I should?
#
# Then it uses the information as parameters for LDA.

import os
import sys
import math
import time
import sqlite3
import operator
import threading
import multiprocessing

from gensim import corpora, models, similarities

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
    # Calculate Term Frequencies for this id/document.
    # let's make a short list of the words we'll accept.

    # only words that are greater than one letter and not in the stopword list.
    pruned = [w for w in users_tweets[id].split(' ') if w not in stopwords and len(w) > 1]

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

def threadMain(database_file, output_folder, users, users_tweets, stopwords, start, cnt):
  """
  What, what! : )
  """

  # -------------------------------------------------------------------------
  # Process this thread's users.
  for u in xrange(start, start + cnt):
    user_id = users[u]
    docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values
    output = "%d\t%d\t%.3f\t%.3f\t%d\t%fm"

    start = time.clock()

    curr_cnt = len(users_tweets[user_id])

    docTfIdf = buildDocTfIdf(users_tweets[user_id], stopwords)

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

    with open(os.path.join(output_folder, "%d.tfidf" % user_id), "w") as f:
      f.write("user: %d\n#topics: %d\n" % (user_id, len(centroids)))
      # Might be better if I just implement __str__ for Centroids.
      for cen in centroids:
        f.write("%s\n" % centroids[cen].topTerms(10))
      f.write("------------------------------------------------------------\n")
    
    # output from the above
    centroidCount = len(centroids)

    # -------------------------------------------------------------------------
    # Handle data with gensim LDA modeling code.
    # Use the number of centroids as the topic count input.
    # only words that are greater than one letter and not in the stopword list.
    texts = [[word for word in users_tweets[user_id][id].split() if word not in stopwords and len(word) > 1] for id in users_tweets[user_id]]
    
    # -------------------------------------------------------------------------
    # remove words that appear only once
    all_tokens = sum(texts, [])
    tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
    texts = [[word for word in text if word not in tokens_once] for text in texts]
    
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    
    lda = models.ldamodel.LdaModel(
                                   corpus,
                                   id2word=dictionary,
                                   chunksize=100,
                                   passes=20,
                                   num_topics=centroidCount)

    topic_strings = lda.show_topics(topics=-1, formatted=True)
    
    with open(os.path.join(output_folder, "%d.lda" % user_id), "w") as f:
      f.write("user: %d\n#topics: %d\n" % (user_id, len(topic_strings)))
      for topic in topic_strings: # could use .join
        f.write("%s\n" % str(topic))

    duration = (time.clock() - start) / 60 # for minutes

    print output % \
      (user_id, curr_cnt, average_sim, stddev_sim, centroidCount, duration)

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
    "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
  # "select id, contents as text from tweets where owner = %d;"
  query_prefect = \
    "select owner, id, contents as text from tweets where owner in (%s);"

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()
  
  print "#cpus: %d" % cpus

  # ---------------------------------------------------------------------------
  # Search the database file for users.
  users = []
  users_tweets = {}

  start = time.clock()

  query = query_prefect % query_collect

  for row in c.execute(query % (minimum, maximum)):
    uid = row['owner']
    if uid not in users:
      users.append(uid)
    if row['text'] is not None:
      data = TweetClean.cleanup(row['text'], True, True)
      try:
        users_tweets[uid][row['id']] = data
      except KeyError:
        users_tweets[uid] = {}
        users_tweets[uid][row['id']] = data

  print "query time: %fm" % ((time.clock() - start) / 60)
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

    print "launching thread: %d, %d" % (start, cnt)

    t = threading.Thread(
                         target=threadMain,
                         args=(
                               database_file,
                               output_folder,
                               users,
                               users_tweets,
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

