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

sys.path.append("tweetlib")
sys.path.append("modellib")
import TweetClean
import TweetDate
import VectorSpace

def usage():
	print "usage: %s <input file> <out:matrix file> <out:similarity file>" % sys.argv[0]

def main():
	# Weirdly in Python, you have free access to globals from within main().

	hourlyInterval = 0 # are we building hourly or daily histograms?
	totalTermCount = 0 # total count of all terms
	cleanTweets = {}   # dictionary of the tweets by id as integer

	docFreq = {}       # dictionary of in how many documents the "word" appears
	invdocFreq = {}    # dictionary of the inverse document frequencies
	docTermFreq = {}   # dictionary of term frequencies by date as integer
	docTfIdf = {}      # similar to docTermFreq, but holds the tf-idf values

	# Did they provide the correct args?
	if len(sys.argv) != 4:
		usage()
		sys.exit(-1)

	# Pull lines
	with open(sys.argv[1], "r") as f:
		tweets = f.readlines()

	print "tweets: %d" % len(tweets)

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
			sys.exit(-1)

		# Do some cleanup
		# Add this tweet to the collection of clean ones.
		cleanTweets[info[0]] = TweetClean.cleanup(info[1])

	# End of: "for i in tweets:"
	# Thanks to python and not letting me use curly braces.

	# ---------------------------------------------------------------------------
	# Process the collected tweets
	print "tweet days: %d" % len(cleanTweets)
	for id in cleanTweets.keys():
		docTermFreq[id] = {} # Prepare the dictionary for that document.
		
		# Calculate Term Frequencies for this id/document.
		# Skip 1 letter words.
		words = cleanTweets[id].split(' ')
		for w in words:
			if len(w) > 1:
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
	# Dump how many days of tweets we collected.
	# For each id of tweets, dump how many unique terms were identified by space splitting.
	#
	print "sizeof documents: %d" % totalTermCount
	print "sizeof docFreq: %d" % len(docFreq)         # this is how many unique terms
	print "sizeof docTermFreq: %d" % len(docTermFreq) # this is how many days

	for id in docTermFreq:
		print "sizeof docTermFreq[%s]: %d" % (str(id), len(docTermFreq[id])) # this is how many unique terms were in that id
		#print docTermFreq[id]
	
	# Calculate the inverse document frequencies.
	invdocFreq = VectorSpace.calculate_invdf(len(docTermFreq), docFreq)
	
	# Calculate the tf-idf values.
	docTfIdf = VectorSpace.calculate_tfidf(totalTermCount, docTermFreq, invdocFreq)

	# Recap of everything we have stored.
	# totalTermCount is the total count of all terms
	# cleanTweets    is the dictionary of the tweets by id as string
	# docFreq        is the dictionary of in how many documents the "word" appears
	# invdocFreq     is the dictionary of the inverse document frequencies
	# docTermFreq    is the dictionary of term frequencies by date as integer
	# docTfIdf       is similar to docTermFreq, but holds the tf-idf values

	# Dump the matrix.
	with open(sys.argv[2], "w") as f:
		f.write(VectorSpace.dumpMatrix(docFreq, docTfIdf) + "\n")

	# Computer cosine similarities between sequential days.
	sorted_docs = sorted(docTfIdf.keys())
	with open(sys.argv[3], "w") as f:
		for i in xrange(0, len(sorted_docs) - 1):
			f.write("similarity(%s, %s) = " % (str(sorted_docs[i]), str(sorted_docs[i+1])))
			f.write(str(VectorSpace.cosineCompute(docTfIdf[sorted_docs[i]], docTfIdf[sorted_docs[i+1]])) + "\n")

	# ---------------------------------------------------------------------------
	# Done.

if __name__ == "__main__":
  main()

