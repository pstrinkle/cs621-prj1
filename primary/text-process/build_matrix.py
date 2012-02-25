#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012


import os
import sys
import sqlite3

sys.path.append(os.path.join("..", "tweetlib"))
import TweetClean

sys.path.append(os.path.join("..", "modellib"))
import vectorspace

def usage():
  print "%s <database_file> <minimum> <maximum> <stop_file> <output>" % sys.argv[0]

def main():

  if len(sys.argv) != 6:
    usage()
    sys.exit(-1)

  # ---------------------------------------------------------------------------
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

  print kickoff % (database_file, minimum, maximum, output_file, stop_file) 

  # this won't return the 3 columns we care about.
  query_collect = \
    "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
  # "select id, contents as text from tweets where owner = %d;"
  query_prefetch = \
    "select owner, id, contents as text from tweets where owner in (%s);"
    
  query = query_prefetch % query_collect

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()
  
  user_tweets = {}
  
  for row in c.execute(query % (minimum, maximum)):
    if row['text'] is not None:
      data = TweetClean.cleanup(row['text'], True, True)
      try:
        user_tweets[row['owner']].append(data)
      except KeyError:
        user_tweets[row['owner']] = []
        user_tweets[row['owner']].append(data)

  conn.close()

  # ---------------------------------------------------------------------------
  # Convert to a documents into one document per user.

  docperuser = {} # array representing all the tweets for each user.

  for user_id in user_tweets:
    docperuser[user_id] = "".join(user_tweets[user_id])

  tfidf, dictionary = vectorspace.buildDocTfIdf(docperuser, stopwords, True)

  # Dump the matrix.
  with open(output_file, "w") as f:
    f.write(vectorspace.dumpMatrix(dictionary, tfidf) + "\n")

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()