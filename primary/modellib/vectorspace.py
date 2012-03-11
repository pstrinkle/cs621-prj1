#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Summer 2011
# Spring 2012
#
# @summary: This handles the vector space model stuff.
#

import math

def calculate_invdf(doc_count, doc_freq):
    """
    Calculate the inverse document frequencies.
  
    The inverse document frequency is how many documents there are divided by 
    in how many documents the term appears.
  
    Input: doc_count := number of documents
        doc_freq := dictionary of document frequencies, key'd by term
  
    Output: invdoc_freq := dictionary of inverse document frequencies, key'd by 
                        term
  
    idf = log(document count / in how many documents)
    """
  
    invdoc_freq = {}
  
    for term in doc_freq:
        invdoc_freq[term] = math.log10(float(doc_count) / doc_freq[term])

    return invdoc_freq

def calculate_tfidf(doc_length, doc_termfreq, invdoc_freq):
    """
    Calculate the tf-idf values.
  
    Input: doc_length := total frequency (not distinct count), key'd on doc id
         doc_termfreq := dictionary of term frequencies, key'd on document, 
                         then key'd by term.
         invdoc_freq := dictionary of inverse document frequencies, key'd on 
                        term.
         
    Output: doc_tfidf := dictionary of tf-idf values, key'd on document
  
    A high weight in tf-idf is reached by a high term frequency (in the given 
    document) and a low document frequency of the
    # term in the whole collection of documents.
  
    td-idf = 
        (term count / count of all terms in document) 
            * log(document count / in how many documents)
    """

    doc_tfidf = {}

    for doc in doc_termfreq.keys():
        doc_tfidf[doc] = {} # Prepare the dictionary for that document.
        for w in doc_termfreq[doc]:
            doc_tfidf[doc][w] = (float(doc_termfreq[doc][w]) / doc_length[doc]) * invdoc_freq[w]

    return doc_tfidf

def cosine_compute(vector_a, vector_b):
    """
    Compute the cosine similarity of two normalized vectors.
    vector_a and vector_b are dictionaries, where the key is the term and the value
    is the tf-idf.
    """
    dotproduct = 0.0
  
    for k in vector_a.keys():
        if k in vector_b.keys():
            dotproduct += vector_a[k] * vector_b[k]
  
    return dotproduct

def dump_raw_matrix(term_dict, tfidf_dict):
    """
    Dump a complete term space matrix of tf-idf values.

    The printout should look something like:

    w1,  w2,  w3,  wN
    w1,  w2,  w3,  wN
    w1,  w2,  w3,  wN
  
    Which is an NxM matrix.  It will be a sparse matrix for most cases.
    """

    output = ""
  
    sorted_docs = sorted(tfidf_dict.keys())  
    sorted_terms = sorted(term_dict)
  
    # Print Term Rows
    for t in sorted_terms:
        for d in sorted_docs:
            if t in tfidf_dict[d]:
                output += str(tfidf_dict[d][t]) + ","
            else:
                output += str(0.0) + ","
        output += "\n"

    return output

def dump_matrix(term_dict, tfidf_dict):
    """
    Dump a complete term space matrix of tf-idf values.
  
    The printout should look something like:
    terms,day1,day2,day3,...,dayN
    t1,   w1,  w2,  w3,  wN
    t2,   w1,  w2,  w3,  wN
    tM,   w1,  w2,  w3,  wN
  
    Which is an NxM matrix.  It will be a sparse matrix for most cases.
    """

    output = ""

    sorted_docs = sorted(tfidf_dict.keys())  
    sorted_terms = sorted(term_dict)
  
    # Print Matrix!
    output += "term weight space matrix!\n"

    # Print Header Row
    output += "terms,"
    for d in sorted_docs:
        output += str(d) + ","
    output += "\n"
  
    # Print Term Rows
    for t in sorted_terms:
        output += t + ","
        for d in sorted_docs:
            if t in tfidf_dict[d]:
                output += str(tfidf_dict[d][t]) + ","
            else:
                output += str(0.0) + ","
        output += "\n"

    return output

def build_doc_tfIdf(documents, stopwords, remove_singletons=False):
    """
    Note: This doesn't remove singletons from the dictionary of terms, unless 
    you say otherwise.  With tweets there is certain value in not removing 
    singletons.
  
    Input:
        documents := a dictionary of documents, by an doc_id value.
        stopwords := a list of stopwords.
        remove_singletons := boolean value of whether we should remove stop 
                             words.

    Returns:
        document tf-idf vectors.
        term counts
    """
    
    if len(documents) == 1:
        print "WARNING: Computing on 1 document means all will be singletons."

    doc_length = {}   # total count of all terms, keyed on document
    doc_freq = {}     # dictionary of in how many documents the "word" appears
    doc_termfreq = {} # dictionary of term frequencies by date as integer

    for doc_id in documents:
        # Calculate Term Frequencies for this doc_id/document.
        # let's make a short list of the words we'll accept.

        # only words that are greater than one letter and not in the stopword list.
        pruned = [w for w in documents[doc_id].split(' ') if w not in stopwords and len(w) > 1]

        if len(pruned) < 2:
            continue

        doc_termfreq[doc_id] = {} # Prepare the dictionary for that document.

        try:
            doc_length[doc_id] += len(pruned)
        except KeyError:
            doc_length[doc_id] = len(pruned)

        for w in pruned:
            try:
                doc_termfreq[doc_id][w] += 1
            except KeyError:
                doc_termfreq[doc_id][w] = 1

        # Contribute to the document frequencies.
        for w in doc_termfreq[doc_id]:
            try:
                doc_freq[w] += 1
            except KeyError:
                doc_freq[w] = 1

    if remove_singletons:
        singles = [w for w in doc_freq.keys() if doc_freq[w] == 1]
        # could use map() function to delete terms from singles
        for doc_id in doc_termfreq:
            for s in singles:
                try:
                    del doc_termfreq[doc_id][s]
                    doc_length[doc_id] -= 1 # only subtracts if the deletion worked
                except KeyError:
                    pass

    #print "document frequency: %s" % doc_freq
    #print "term frequency per document: %s" % doc_termfreq
      
    # Calculate the inverse document frequencies.
    # dictionary of the inverse document frequencies
    invdoc_freq = calculate_invdf(len(doc_termfreq), doc_freq)
    
    #print "inverse document frequency: %s" % invdoc_freq

    # Calculate the tf-idf values.
    # similar to doc_termfreq, but holds the tf-idf values
    doc_tfidf = calculate_tfidf(doc_length, doc_termfreq, invdoc_freq)
    
    #print "tf-idf per document: %s" % doc_tfidf

    return doc_tfidf, doc_freq

class DocumentStore:
    """
    In the future it may become useful to store information about the documents.
  
    So that the model an be updated.
    """
    def __init__(self, name):
        self.name = name
