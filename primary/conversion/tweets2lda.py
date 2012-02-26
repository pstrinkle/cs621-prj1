#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# Given one of my tweet XML repos, this formats the data to be input for Prof 
# Blei's LDA-C code.
#
# Under LDA, the words of each document are assumed exchangeable. 
# Thus, each document is succinctly represented as a sparse vector of word 
# counts.
#
# The data is a file where each line is of the form:
# [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]
# where [M] is the number of unique terms in the document, and the [count] 
# associated with each term is how many times that term appeared in the 
# document.  Note that [term_1] is an integer which indexes the term; it is not 
# a string.

import sys
import sqlite3

sys.path.append("tweetlib")
import tweetdate
import tweetclean

def getIndx(vocab, term):
    """
    Given a vocabulary array and a term, return the index into the array; returns
      -1 if not present.
    """
    for i in xrange(len(vocab)):
        if term == vocab[i]:
            return i

    return -1

def usage():
    print "usage: %s <database> <user_id> <input stopwords> <out:vocab> <out:dat>" % \
        sys.argv[0]

def main():

    # Did they provide the correct args?
    if len(sys.argv) != 6:
        usage()
        sys.exit(-1)
    
    database_file = sys.argv[1]
    user_id = int(sys.argv[2])
    stop_file = sys.argv[3]
    outputvocab = sys.argv[4]
    outputdata = sys.argv[5]    

    # ---------------------------------------------------------------------------
    # Pull stop words
    stopwords = tweetclean.importStopWords(stop_file)

    # ---------------------------------------------------------------------------
    # Read in the database
    query_tweets = "select id, contents as text from tweets where owner = %d;"
    users_tweets = {}
    docTermFreq = {}   # dictionary of term frequencies by date as integer
    vocab = []         # array of terms
    
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    for row in c.execute(query_tweets % user_id):
        users_tweets[row['id']] = row['text']

    conn.close()

    # ---------------------------------------------------------------------------
    # Process tweets
    for id in users_tweets:

        if users_tweets[id] == None: # this happens, lol.
            continue

        users_tweets[id] = tweetclean.cleanup(users_tweets[id], True, True)
        
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
            try:
                docTermFreq[id][w] += 1
            except KeyError:
                docTermFreq[id][w] = 1
            
            if w not in vocab: # slow. linear search... maybe switch to a sorted method?
                vocab.append(w)
    
    vocab.sort()
    
    # ---------------------------------------------------------------------------
    # Build the vocab.txt file
    with open(outputvocab, 'w') as f:
        f.write("\n".join(vocab))
    
    # ---------------------------------------------------------------------------
    # Given the vocab array, build the document term index + counts:
    sorted_tweets = sorted(users_tweets.keys())
    
    data = ""
    
    for id in sorted_tweets:
        try:
            lens = len(docTermFreq[id])
        except:
            continue

        print "%d" % id
        data += "%d " % lens
        
        for term in docTermFreq[id]:
            indx = getIndx(vocab, term)
            if indx == -1:
                sys.exit(-1)
            data += "%d:%d " % (indx, docTermFreq[id][term])
            
        data += "\n"

    with open(outputdata, "w") as f:
        f.write(data)

    # ---------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
