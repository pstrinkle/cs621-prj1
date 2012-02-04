#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# This tries to build a word level histogram (sketch) for each
# day's tweets.
# OR
# This tries to build a word level histogram (sketch) for each
# hour's tweets.
#
# This opens the xml file holding the tweets, and builds a giant
# tweet for each day, by appending the previous day's tweets.
#
# My goal is tokenize the string and then remove the words that aren't.
#

import os
import sys

sys.path.append("tweetlib")
sys.path.append("modellib")
import TweetClean
import TweetDate
import VectorSpace

def usage():
  print "usage: %s (daily|hourly) <input file> <out:matrix file> <out:similarity file>" % sys.argv[0]

def main():
  # Weirdly in Python, you have free access to globals from within main().

  hourlyInterval = 0 # are we building hourly or daily histograms?
  totalTermCount = 0 # total count of all terms
  daysTweets = {}    # dictionary of the tweets by date as integer
                     # dictionary of the tweets by date-hour as integer
                     
  docFreq = {}       # dictionary of in how many documents the "word" appears
  invdocFreq = {}    # dictionary of the inverse document frequencies
  docTermFreq = {}   # dictionary of term frequencies by date as integer
  docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values

  # Did they provide the correct args?
  if len(sys.argv) != 5:
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
    # Each tweet has <created>DATE-TIME</created> and <text>DATA</text>.
    #
    # So we'll have a dictionary<string, string> = {"date", "contents"}
    #
    # So, we'll just append to the end of the string for the dictionary
    # entry.
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

    # Add this tweet to the collective tweet for the day.
    if date in daysTweets:
      daysTweets[date] += " " + newTweet
    else:
      daysTweets[date] = newTweet

  # End of: "for i in tweets:"
  # Thanks to python and not letting me use curly braces.

  # ---------------------------------------------------------------------------
  # Process the collected tweets
  print "tweet days: %d" % len(daysTweets)
  for day in daysTweets.keys():
    docTermFreq[day] = {} # Prepare the dictionary for that document.
    
    # Calculate Term Frequencies for this day/document.
    # Skip 1 letter words.
    words = daysTweets[day].split(' ')
    for w in words:
      if len(w) > 1:
        totalTermCount += 1
        
        try:
          docTermFreq[day][w] += 1
        except KeyError:
          docTermFreq[day][w] = 1

    # Contribute to the document frequencies.
    for w in docTermFreq[day]:
      try:
        docFreq[w] += 1
      except KeyError:
        docFreq[w] = 1

  # ---------------------------------------------------------------------------
  # Dump how many unique terms were identified by spacing splitting.
  # Dump how many days of tweets we collected.
  # For each day of tweets, dump how many unique terms were identified by space splitting.
  #
  print "sizeof documents: %d" % totalTermCount
  print "sizeof docFreq: %d" % len(docFreq)         # this is how many unique terms
  print "sizeof docTermFreq: %d" % len(docTermFreq) # this is how many days

  for day in docTermFreq:
    print "sizeof docTermFreq[%s]: %d" % (str(day), len(docTermFreq[day])) # this is how many unique terms were in that day
    #print docTermFreq[day]
  
  # Calculate the inverse document frequencies.
  invdocFreq = VectorSpace.calculate_invdf(len(docTermFreq), docFreq)
  
  # Calculate the tf-idf values.
  docTfIdf = VectorSpace.calculate_tfidf(totalTermCount, docTermFreq, invdocFreq)

  # Recap of everything we have stored.
  # totalTermCount is the total count of all terms
  # daysTweets     is the dictionary of the tweets by date as integer
  # docFreq        is the dictionary of in how many documents the "word" appears
  # invdocFreq     is the dictionary of the inverse document frequencies
  # docTermFreq    is the dictionary of term frequencies by date as integer
  # docTfIdf       is similar to docTermFreq, but holds the tf-idf values

  # Sort the lists by decreasing value and dump the information.
  # TODO: Upgrade this to print the top 15-20 or so.
  sorted_keys = docTfIdf.keys()
  sorted_keys.sort()
  print "token:weight"
  for day in sorted_keys:
    print str(day) + ":---"
    sorted_tokens = [(v, k) for k, v in docTfIdf[day].items()]
    sorted_tokens.sort()
    sorted_tokens.reverse()
    sorted_tokens = [(k, v) for v, k in sorted_tokens]
    for k, v in sorted_tokens:
      print k + ":" + str(v)

  # Dump the matrix.
  with open(sys.argv[3], "w") as f:
    f.write(VectorSpace.dumpMatrix(docFreq, docTfIdf) + "\n")

  # Computer cosine similarities between sequential days.
  sorted_days = sorted(docTfIdf.keys())
  with open(sys.argv[4], "w") as f:
    # -1 because each goes +1
    for i in xrange(0, len(sorted_days) - 1):
      f.write("similarity(%s, %s) = " % (str(sorted_days[i]), str(sorted_days[i+1])))
      f.write(str(VectorSpace.cosineCompute(docTfIdf[sorted_days[i]], docTfIdf[sorted_days[i+1]])) + "\n")

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
