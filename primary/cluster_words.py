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
import Centroid

def usage():
	print "usage: %s <input file>" % sys.argv[0]

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
	if len(sys.argv) != 2:
		usage()
		sys.exit(-1)

	# Pull lines
	with open(sys.argv[1], "r") as f:
		tweets = f.readlines()

	#print "tweets: %d" % len(tweets)

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
	#print "tweet days: %d" % len(cleanTweets)
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
	print "Total Count of Terms: %d" % totalTermCount
	print "Unique Terms: %d" % len(docFreq)           # this is how many unique terms
	print "How many Documents: %d" % len(docTermFreq) # this is how many days

	#for id in docTermFreq:
		#print "sizeof docTermFreq[%s]: %d" % (str(id), len(docTermFreq[id])) # this is how many unique terms were in that id
		#print docTermFreq[id]
	
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

	# Build Centroid List
	centroids = []
	
	for doc, vec in docTfIdf.iteritems():
		centroids.append(Centroid.Centroid(str(doc), vec))
	
	#print "sizeof(centroids): %d" % len(centroids)
	#for cen in centroids:
		#if cen.name not in docTfIdf:
			#print "bad"
	
	threshold = 0.025
	deleted = False

	# Not 100% satisfied with this method.  I should search for the maximum similarity
	# and then repeat this process, as my c# program does.
	while len(centroids) > 1:
		print "while!"
		# did we fully loop?
		if i == (len(centroids) - 1) and j == (len(centroids) - 1):
			break
		
		deleted = False
		
		for i in xrange(0, len(centroids) - 1):
			for j in xrange(0, len(centroids) - 1):
				if i != j:
					curr_sim = Centroid.similarity(centroids[i], centroids[j])
					print "curr_sim: %f" % curr_sim
					if curr_sim >= threshold:
						print "above threshold merger, %s, %s" % (centroids[i].name, centroids[j].name)
						centroids[i].addVector(centroids[j].name, centroids[j].vectorCnt, centroids[j].centroidVector)
						del centroids[j]
						deleted = True
						break
					else:
						print "not above"
			if deleted: # if inner loop deleted, then try again from outer loop.
				print "should break to while"
				break


	# ---------------------------------------------------------------------------
	# - Disabled code start -- just finds closest tweet and merges.
	# Compute all similarities
	#max_sim = 0.0
	#max_nameA = ""
	#max_nameB = ""
	#max_i = 0
	#max_j = 0

	#for i in xrange(0, len(centroids) - 1):
		#for j in xrange(0, len(centroids) - 1):
			#if i != j:
				#curr_sim = Centroid.similarity(centroids[i], centroids[j])
				#if curr_sim > max_sim:
					#max_sim = curr_sim
					#max_nameA = centroids[i].name
					#max_nameB = centroids[j].name
					#max_i = i
					#max_j = j
				#print "similarity %f" % curr_sim
	
	#print "%f\n%s (%d) v %s (%d)" % (max_sim, max_nameA, max_i, max_nameB, max_j)
	#print "'%s' -- '%s'" % (cleanTweets[max_nameA], cleanTweets[max_nameB])
	#print "i: %f\nj: %f" % (centroids[max_i].length, centroids[max_j].length)

	#centroids[max_i].addVector(centroids[max_j].name, 1, centroids[max_j].centroidVector)
	#del centroids[max_j]
	
	#print "merged: %f\nmerged: '%s'" % (centroids[max_i].length, centroids[max_i].name)
	# - End Disabled code region.

	# ---------------------------------------------------------------------------
	# Done.

if __name__ == "__main__":
  main()

