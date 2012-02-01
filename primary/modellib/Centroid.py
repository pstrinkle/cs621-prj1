#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles representing/storing document centroids in a vector space model.
#

import math

def similarity(a, b):
    """
    Compute dot product of vectors A & B
    """
    vectorA = a.centroidVector
    vectorB = b.centroidVector
    
    lengthA = a.length
    lengthB = b.length
    
    dotproduct = 0.0

    for key, value in vectorA.iteritems():
      if key in vectorB: # if both vectors have the key
        dotproduct += (value * vectorB[key])

    return float(dotproduct / (lengthA * lengthB))

def topTerms(a, n):
  """
  Returns the n-highest tf-idf terms in the vector.
  """
  sorted_tokens = [(v, k) for k, v in a.centroidVector.items()]
  sorted_tokens.sort()
  sorted_tokens.reverse()
  sorted_tokens = [(k, v) for v, k in sorted_tokens]
  
  print "len(sorted_tokens): %d" % len(sorted_tokens)
  
  # count to index
  to_print = min(n, len(sorted_tokens))
  top_terms = []
  
  print "to_print: %d" % to_print
  
  for i in xrange(0, to_print):
    top_terms.append(sorted_tokens[i])

  return top_terms

class Centroid:
  """
  This data structure represents an average of documents in a vector space.
  
  Amusingly, modeled directly after a C# class I wrote for a class I took.
  """
  
  def __init__(self, name, dv):
    """
    Representation of a document(s) as a tf-idf vector.
    
    name the name for it.
    """
    self.name = "" # it's added below
    self.vectorCnt = 0
    self.centroidVector = {}
    self.length = 0.00
    self.addVector(name, 1, dv)
    

  def __len__(self):
    """
    Get the length of it!
    """
    return len(self.centroidVector)

  def addVector(self, docName, addCnt, newDocVec):
    """
    This averages in the new vector.
    
    docName := the name of the thing we're adding in.
    addCnt  := the number of documents represented by newV.
    newV    := the vector representing the document(s).
    
    This is copied and translated directly from my c# program.
    """
    
    # determine the weight of the merging pieces
    oldWeight = float(self.vectorCnt) / (self.vectorCnt + addCnt)
    newWeight = float(addCnt) / (self.vectorCnt + addCnt)
    
    if len(self.name) == 0:
      self.name = docName
    else:
      self.name += ", %s" % docName
    
    # calculate new centroid
    centroidTerms = list(self.centroidVector.keys())
    
    # reduce weight of values already in vector
    for key in centroidTerms:
      if key in newDocVec: # if is in both vectors!
        oldValue = float(self.centroidVector[key]) * oldWeight
        newValue = float(newDocVec[key]) * newWeight
        
        self.centroidVector[key] = oldValue + newValue
        
        # so when we go through to add in all the missing ones we won't have excess
        del newDocVec[key]
      else: # if it is strictly in the old vector
        oldValue = float(self.centroidVector[key]) * oldWeight
        self.centroidVector[key] = oldValue
    
    # add new values to vector
    for key, value in newDocVec.iteritems():
      # we don't so we'll have to create a new value with the weight of the added vector
      self.centroidVector[key] = float(value) * newWeight

    self.vectorCnt += addCnt
    self.length = 0
    
    # calculate magnitude
    for key, value in self.centroidVector.iteritems():
      self.length += (value * value)
    
    self.length = math.sqrt(self.length)
    
