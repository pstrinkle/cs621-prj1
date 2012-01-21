#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Given one of my tweet XML repos, this formats the data to be input for Prof Blei's LDA-C code.
#
# Under LDA, the words of each document are assumed exchangeable. 
# Thus, each document is succinctly represented as a sparse vector of word counts.
#
# The data is a file where each line is of the form:
# [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]
# where [M] is the number of unique terms in the document, and the [count] associated with each 
# term is how many times that term appeared in the document.  Note that [term_1] is an 
# integer which indexes the term; it is not a string.

import sys

sys.path.append("tweetlib")
import TweetDate
import TweetClean

def getIndx(vocab, term):
  """
  Given a vocabulary array and a term, return the index into the array; returns -1 if not present.
  """
  for i in range(len(vocab)):
    if term == vocab[i]:
      return i

  return -1

def usage():
  print "usage: %s <input xml> <input stopwords> <out:vocab> <out:dat>" % sys.argv[0]

def main():

  # Did they provide the correct args?
  if len(sys.argv) != 5:
    usage()
    sys.exit(-1)

  daysTweets = {}      # dictionary of the tweets by date-hour as integer
  daysTweetsTerms = {} # dictionary of the tweets as a set of terms and their counts by date-hour as integer
  vocab = []           # array of terms

  # ---------------------------------------------------------------------------
  # Read in the XML file, pulling out the tweets
  with open(sys.argv[1], "r") as f:
    tweets = f.readlines()
  
  with open(sys.argv[2], "r") as f:
    stopwordsstr = f.read()
  stopwords = stopwordsstr.split("\n")
  
  outputvocab = sys.argv[3]
  outputdata = sys.argv[4]

  # ---------------------------------------------------------------------------
  # Process tweets
  for i in tweets:
    info = TweetClean.extract(i)
    if info == None:
      sys.exit(-1)
    
    # Build day string
    # This needs to return -1 on error, so I'll need to test it.
    date = TweetDate.buildDateInt(info[0])

    # Do some cleanup
    newTweet = TweetClean.cleanup(info[1])
    
    # Add this tweet to the collective tweet for the day.
    if date in daysTweets:
      daysTweets[date] += " " + newTweet
    else:
      daysTweets[date] = newTweet
      daysTweetsTerms[date] = {}
  
  # ---------------------------------------------------------------------------
  # Build the vocab.txt file
  for day in daysTweets.keys():
    for term in daysTweets[day].split(' '):
      
      if term == ' ' or term == '' or term in stopwords or len(term) == 1:
        continue
      
      if term not in daysTweetsTerms[date]:
        daysTweetsTerms[date][term] = 0
      daysTweetsTerms[date][term] += 1

      if term not in vocab:
        vocab.append(term)

  # TODO: I am still getting a weird term.
  #print "sizeof(vocab): %d" % len(vocab)
  # with syntax started in 2.6 or 2.7; for 2.4 use normal open/write/close.
  with open(outputvocab, 'w') as f:
    f.write("\n".join(vocab))
  
  # ---------------------------------------------------------------------------
  # Given the vocab array, build the document term index + counts:
  sorted_days = daysTweets.keys()
  sorted_days.sort()
  
  data = ""
  
  for day in sorted_days:
    print "%d" % day
    data += "%d " % len(daysTweetsTerms[date])
    
    for term in daysTweetsTerms[date]:
      indx = getIndx(vocab, term)
      if indx == -1:
        sys.exit(-1)
      data += "%d:%d " % (indx, daysTweetsTerms[date][term])
      
    data += "\n"

  with open(outputdata, "w") as f:
    f.write(data)

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
