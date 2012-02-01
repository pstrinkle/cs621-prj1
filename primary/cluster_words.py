#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This tries to cluster the tweets by topic.
#
# This opens the xml file holding the tweets, and builds a giant
# tweet for each day, by appending the previous day's tweets.
#
# My goal is tokenize the string and then remove the words that aren't.
#
# select count(*), owner from tweets group by owner having count(*) > 1000;
#
# The input for this program can be found by running pull_from_database.py.

import os
import sys
import codecs

sys.path.append("tweetlib")
sys.path.append("modellib")
import TweetClean
import TweetDate
import VectorSpace
import Centroid

def usage():
  """
  Standard usage method.
  """
  print "usage: %s <tweet file> <stopwords file>" % sys.argv[0]

def findAvg(centroids):
  """
  Given a list of Centroids, compute the similarity of each pairing and return the
  average.
  """
  total_sim = 0.0
  total_comparisons = 0

  for i in xrange(0, len(centroids)):
    for j in xrange(0, len(centroids)):
      if i != j: 
        total_sim += Centroid.similarity(centroids[i], centroids[j])
        total_comparisons += 1

  return (total_sim / total_comparisons)

def findMax(centroids):
  """
  Given a list of Centroids, compute the similarity of each pairing and return the
  pair with the highest similarity, and their similarity score--so i don't have to 
  re-compute.
  """
  max_sim = 0.0
  max_i = 0
  max_j = 0

  for i in xrange(0, len(centroids)):
    for j in xrange(0, len(centroids)):
      if i != j:
        curr_sim = Centroid.similarity(centroids[i], centroids[j])
        if curr_sim > max_sim:
          max_sim = curr_sim
          max_i = i
          max_j = j

  return (max_i, max_j, max_sim)

def main():

  totalTermCount = 0 # total count of all terms
  cleanTweets = {}   # dictionary of the tweets by id as integer

  docFreq = {}       # dictionary of in how many documents the "word" appears
  invdocFreq = {}    # dictionary of the inverse document frequencies
  docTermFreq = {}   # dictionary of term frequencies by date as integer
  docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values

  # Did they provide the correct args?
  if len(sys.argv) != 3:
    usage()
    sys.exit(-1)

  # Pull lines
  with codecs.open(sys.argv[1], "r", 'utf-8') as f:
    tweets = f.readlines()

  # Pull stop words
  with open(sys.argv[2], "r") as f:
    stopwords = f.readlines()

  # clean them up!
  for i in xrange(0, len(stopwords)):
    stopwords[i] = stopwords[i].strip()

  # ---------------------------------------------------------------------------
  # Process tweets
  for i in tweets:
    # Each tweet has <id>DATE-TIME</id> and <text>DATA</text>.
    #
    # So we'll have a dictionary<string, string> = {"id", "contents"}
    #
    # So, we'll just append to the end of the string for the dictionary
    # entry.
    info = TweetClean.extract_id(i)
    if info == None:
      sys.stderr.write("Invalid tweet hit\n")
      sys.exit(-1)

    if len(info[1]) < 3:
      print info[1]
      sys.exit(0)

    # Add this tweet to the collection of clean ones.
    cleanTweets[info[0]] = TweetClean.cleanup(info[1], True, True)

  # ---------------------------------------------------------------------------
  # Process the collected tweets
  for id in cleanTweets.keys():
    # Calculate Term Frequencies for this id/document.
    # Skip 1 letter words.
    words = cleanTweets[id].split(' ')

    # let's make a short list of the words we'll accept.
    pruned = []

    for w in words:
      if len(w) > 1 and w not in stopwords:
        pruned.append(w)

    if len(pruned) < 2:
      print "skipping %s" % id
      continue

    docTermFreq[id] = {} # Prepare the dictionary for that document.
    
    for w in pruned:
      if len(w) > 1 and w not in stopwords:
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

  # ---------------------------------------------------------------------------
  # Dump how many unique terms were identified by spacing splitting.
  print "Total Count of Terms: %d" % totalTermCount
  print "Unique Terms: %d" % len(docFreq)           # this is how many unique terms
  print "How many Documents: %d" % len(docTermFreq) # this is how many days

  # Calculate the inverse document frequencies.
  invdocFreq = VectorSpace.calculate_invdf(len(docTermFreq), docFreq)

  # Calculate the tf-idf values.
  docTfIdf = VectorSpace.calculate_tfidf(totalTermCount, docTermFreq, invdocFreq)

  # ---------------------------------------------------------------------------
  # Recap of everything we have stored.
  # totalTermCount is the total count of all terms
  # cleanTweets    is the dictionary of the tweets by id as string
  # docFreq        is the dictionary of in how many documents the "word" appears
  # invdocFreq     is the dictionary of the inverse document frequencies
  # docTermFreq    is the dictionary of term frequencies by date as integer
  # docTfIdf       is similar to docTermFreq, but holds the tf-idf values

  # ---------------------------------------------------------------------------
  # Build Centroid List
  centroids = []

  for doc, vec in docTfIdf.iteritems():
    centroids.append(Centroid.Centroid(str(doc), vec))

  average_sim = findAvg(centroids)
  
  # ---------------------------------------------------------------------------
  # Merge centroids by highest similarity of at least threshold  
  threshold = average_sim

  while len(centroids) > 1:
    i, j, sim = findMax(centroids)

    if sim >= threshold:
      centroids[i].addVector(centroids[j].name, centroids[j].vectorCnt, centroids[j].centroidVector)
      del centroids[j]
      print "merged with sim: %.10f" % sim
    else:
      break

  print "len(centroids): %d" % len(centroids)
  print "avg(centroids): %.10f" % average_sim
  
  for cen in centroids:
    print Centroid.topTerms(cen, 10)

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()

