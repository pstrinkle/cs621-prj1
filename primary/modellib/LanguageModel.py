#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
# Spring 2012
#
# This handles the language model stuff.
#
# Currently implemented for words, Bigram model.

def build_matrix(inputString, invalids=""):
  """
  Given a string, build a matrix of occurrences of pairs of terms.
  
  Input: inputString := string you want to parse
         invalids := string pieces to remove, as single characters in a string
  Output: matrix of occurrences {'termA + "_" + termB' => int}
  
  The matrix is built as a dictionary, key'd by the paired terms. 
  """
  termMatrix = {}
  words = inputString.split(' ')
  
  while ' ' in words:
    words.remove(' ')
  
  while '' in words:
    words.remove('')
  
  for word in words:
    if word in invalids:
      words.remove(word)
  
  # -1 here because we extend each step by +1
  for i in xrange(0, len(words) - 1):
    term = words[i] + "_" + words[i + 1]
    try:
      termMatrix[term] += 1
    except KeyError:
      termMatrix[term] = 1
  
  return termMatrix

def update_matrix(currentMatrix, updateMatrix):
  """
  Given a current matrix and an update matrix, update it!
  
  Input: currentMatrix := current matrix of occurrences
         updateMatrix := update matrix of occurrences

  Output: updated matrix
  
  This should be used in tandem with build_matrix()
  """
  for k, v in updateMatrix.items():
    try:
      currentMatrix[k] += v
    except KeyError:
      currentMatrix[k] = v

  return currentMatrix

class LanguageStore:
  """
  Store the language model, this includes raw data and stats to allow for
  updating.
  
  Currently only works on Bigrams. (pairs of words)
  """

  def __init__(self, initial_document=None):
    self.matrix = None
    self.stats = None
    self.invalids = None
  
  def get_probability(self, seq_bow=""):
    """
    Given a document as a list of words in sequence, return the probability
    of such a sentence given the current state of the model.
    """
    
    return None
  
  def update_model(self, seq_bow=""):
    """
    Add this document to the data used by the model to blah, blah, blah
    """
    
    

