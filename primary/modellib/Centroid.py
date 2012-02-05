#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles representing/storing document centroids in a vector space model.
#

import math
import numpy

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

def getSimMatrix(centroids):
  """
  Given a list of Centroids, compute the similarity score between each
  and return a matrix, matrix[i][j] = 0.000... as a dictionary of dictionaries.

  This function could easily work on a list of them... except then the list 
  would be const, because any manipulation of the centroid list would invalidate
   the matrix.

  XXX: There has to be a cleaner way, since the innermost part of the loop is
  identical...

  XXX: Also, since 4x5 will have the same value as 5x4... I only need to think
  about the upper triangle of values -- see program where i handle this 
  correctly. 
  """
  matrix = {}

  for i in xrange(0, len(centroids)):
    matrix[i] = {}

    for j in xrange(i + 1, len(centroids)):
      matrix[i][j] = similarity(centroids[i], centroids[j])

  return matrix

def getSims(centroids):
  """
  Given a list of Centroids, compute the similarity score between all 
  pairs and return the list.  This can be fed into findAvg(), findStd().
  """

  sims = []
  
  for i in xrange(0, len(centroids)):
    for j in xrange(i + 1, len(centroids)):
      sims.append(similarity(centroids[i], centroids[j]))
  
  return sims

def findStd(centroids, short_cut = False, sim_scores = None):
  """
  Given a list of Centroids, compute the standard deviation of the 
  similarities.
  """
  
  if short_cut:
    return numpy.std(sim_scores)
  
  sims = []
  
  for i in xrange(0, len(centroids)):
    for j in xrange(i + 1, len(centroids)):
      sims.append(similarity(centroids[i], centroids[j]))
  
  return numpy.std(sims)

def findAvg(centroids, short_cut = False, sim_scores = None):
  """
  Given a list of Centroids, compute the similarity of each pairing and return 
  the average.
  
  If short_cut is True, it'll use sim_scores as the input instead of calculating
   the scores.
  """
  total_sim = 0.0
  total_comparisons = 0
  
  if short_cut:
    total_comparisons = len(sim_scores)
    
    for score in sim_scores:
      total_sim += score
    
    return (total_sim / total_comparisons)

  for i in xrange(0, len(centroids)):
    for j in xrange(i + 1, len(centroids)):
      total_sim += similarity(centroids[i], centroids[j])
      total_comparisons += 1

  return (total_sim / total_comparisons)

def findMax(centroids):
  """
  Given a list of Centroids, compute the similarity of each pairing and return 
  the pair with the highest similarity, and their similarity score--so i don't 
  have to re-compute.
  """
  max_sim = 0.0
  max_i = 0
  max_j = 0

  for i in xrange(0, len(centroids)):
    for j in xrange(i + 1, len(centroids)):
      curr_sim = similarity(centroids[i], centroids[j])
      if curr_sim > max_sim:
        max_sim = curr_sim
        max_i = i
        max_j = j

  return (max_i, max_j, max_sim)

def topTerms(a, n):
  """
  Returns the n-highest tf-idf terms in the vector.
  """
  sorted_tokens = [(v, k) for k, v in a.centroidVector.items()]
  sorted_tokens.sort()
  sorted_tokens.reverse()
  sorted_tokens = [(k, v) for v, k in sorted_tokens]
  
  #print "len(sorted_tokens): %d" % len(sorted_tokens)
  
  # count to index
  to_print = min(n, len(sorted_tokens))
  top_terms = []
  
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
    
