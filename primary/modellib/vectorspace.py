#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
# Spring 2012
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

def calculate_tfidf(docLength, docTermFreq, invDocFreq):
  """
  Calculate the tf-idf values.
  
  Input: docLength := total frequency (not distinct count), key'd on doc id
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
        (float(docTermFreq[doc][w]) / docLength[doc]) * invDocFreq[w]

  return docTfIdf

def cosine_compute(vectorA, vectorB):
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

def dump_matrix(term_dict, tfidf_dict):
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

def build_doc_tfIdf(documents, stopwords, remove_singletons=False):
  """
  Note: This doesn't remove singletons from the dictionary of terms, unless you 
  say otherwise.  With tweets there is certain value in not removing singletons.
  
  Input:
    documents := a dictionary of documents, by an docId value.
    stopwords := a list of stopwords.
    remove_singletons := boolean value of whether we should remove stop words.
  
    
  Returns:
    document tf-idf vectors.
    term counts
  """

  docLength = {} # total count of all terms, keyed on document
  docFreq = {}        # dictionary of in how many documents the "word" appears
  docTermFreq = {}    # dictionary of term frequencies by date as integer

  for docId in documents:
    # Calculate Term Frequencies for this docId/document.
    # let's make a short list of the words we'll accept.

    # only words that are greater than one letter and not in the stopword list.
    pruned = [w for w in documents[docId].split(' ') if w not in stopwords and len(w) > 1]

    if len(pruned) < 2:
      continue

    docTermFreq[docId] = {} # Prepare the dictionary for that document.

    try:
      docLength[docId] += len(pruned)
    except KeyError:
      docLength[docId] = len(pruned)

    for w in pruned:
      try:
        docTermFreq[docId][w] += 1
      except KeyError:
        docTermFreq[docId][w] = 1

    # Contribute to the document frequencies.
    for w in docTermFreq[docId]:
      try:
        docFreq[w] += 1
      except KeyError:
        docFreq[w] = 1

  if remove_singletons:
    singles = [w for w in docFreq.keys() if docFreq[w] == 1]
    # could use map() function to delete terms from singles
    for docId in docTermFreq:
      for s in singles:
        try:
          del docTermFreq[docId][s]
          docLength[docId] -= 1 # only subtracts if the deletion worked
        except KeyError:
          pass
      
  # Calculate the inverse document frequencies.
  # dictionary of the inverse document frequencies
  invdocFreq = calculate_invdf(len(docTermFreq), docFreq)

  # Calculate the tf-idf values.
  # similar to docTermFreq, but holds the tf-idf values
  docTfIdf = calculate_tfidf(
                             docLength,
                             docTermFreq,
                             invdocFreq)

  return docTfIdf, docFreq

class DocumentStore:
  """
  In the future it may become useful to store information about the documents.
  
  So that the model an be updated.
  """
  def __init__(self, name):
    self.name = name
