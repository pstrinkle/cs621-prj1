#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This builds a Bigram language model for a given tweet XML file.
#
# Currently implemented for words, Bigram model.

import os
import sys

sys.path.append("tweetlib")
sys.path.append("modellib")
import TweetDate
import TweetClean
import LanguageModel

def usage():
  print "usage: %s (daily|hourly) <input file> <out:matrix file>" % sys.argv[0]

def main():

  hourlyInterval = 0 # are we building hourly or daily histograms?
  rawOccurrenceModel = {} # key'd by term pairing

  # Did they provide the correct args?
  if len(sys.argv) != 4:
    usage()
    sys.exit(-1)

  # Parse command line
  if sys.argv[1] == "hourly":
    hourlyInterval = 1
  elif sys.argv[1] == "daily":
    pass
  else:
    usage()
    sys.exit(-1)

  # Pull lines
  with open(sys.argv[2], "r") as f:
    tweets = f.readlines()

  print "tweets: %d" % len(tweets)
  
  # ---------------------------------------------------------------------------
  # Process tweets
  for i in tweets:
    info = TweetClean.extract(i)
    if info == None:
      sys.exit(-1)

    # Build day string
    # This needs to return -1 on error, so I'll need to test it.
    if hourlyInterval:
      date = TweetDate.buildDateInt(info[0])
    else:
      date = TweetDate.buildDateDayInt(info[0])

    # Do some cleanup
    newTweet = TweetClean.cleanup(info[1])
    
    rawOccurrenceModel = \
      LanguageModel.update_matrix(
                                  rawOccurrenceModel,
                                  LanguageModel.build_matrix(newTweet, "-&"))

  # ---------------------------------------------------------------------------
  # Debug, Dump the Raw Occurrences (not finalized)
  for k, v in rawOccurrenceModel.items():
    print "%s:%d" % (k, v)

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
