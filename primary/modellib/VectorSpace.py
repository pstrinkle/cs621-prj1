#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This handles the vector space model stuff.
#

import math

def calculate_invdf(docCount, docFreq):
  """
  Calculate the inverse document frequencies.
  
  The inverse document frequency is how many documents there are divided by in 
  how many documents the term appears.
  
  Input: docCount := number of documents
         docFreq := dictionary of document frequencies, key'd by term
  
  Output: invdocFreq := dictionary of inverse document frequencies, key'd by 
                        term
  
  idf = log(document count / in how many documents)
  """
  
  invdocFreq = {}
  
  for term in docFreq:
    invdocFreq[term] = math.log10(float(docCount) / docFreq[term])

  return invdocFreq

def calculate_tfidf(totalTermCount, docTermFreq, invDocFreq):
  """
  Calculate the tf-idf values.
  
  Input: totalTermCount := total frequency (not distinct count)
         docTermFreq := dictionary of term frequencies, key'd on document, then
                        key'd by term
         invDocFreq := dictionary of inverse document frequencies, key'd on 
                       term.
         
  Output: docTfIdf := dictionary of tf-idf values, key'd on document
  
  A high weight in tf-idf is reached by a high term frequency (in the given 
  document) and a low document frequency of the
  # term in the whole collection of documents.
  
  td-idf =
    (term count / count of all terms) 
      * log(document count / in how many documents)
  """

  docTfIdf = {}

  for doc in docTermFreq.keys():
    docTfIdf[doc] = {} # Prepare the dictionary for that document.
    for w in docTermFreq[doc]:
      docTfIdf[doc][w] = \
        (float(docTermFreq[doc][w]) / totalTermCount) * invDocFreq[w]

  return docTfIdf

def cosineCompute(vectorA, vectorB):
  """
  Compute the cosine similarity of two normalized vectors.
  vectorA and vectorB are dictionaries, where the key is the term and the value
  is the tf-idf.
  """
  dotproduct = 0.0
  
  for k in vectorA.keys():
    if k in vectorB.keys():
      dotproduct += vectorA[k] * vectorB[k]
  
  return dotproduct

def dumpMatrix(term_dict, tfidf_dict):
  """
  Dump a complete term space matrix of td-idf values.
  
  The printout should look something like:
  terms,day1,day2,day3,...,dayN
  t1,   w1,  w2,  w3,  wN
  t2,   w1,  w2,  w3,  wN
  tM,   w1,  w2,  w3,  wN
  
  Which is an NxM matrix.  It will be a sparse matrix for most cases.
  """

  output = ""

  sorted_docs = sorted(tfidf_dict.keys())  
  sorted_terms = sorted(term_dict.keys())
  
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
