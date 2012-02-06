#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles representing/storing document centroids in a vector space model.
#
# Originally I was calling len(centroids) in each function as input to xrange,
# but I honestly have no idea whether that is being re-evaluated each time or
# whether or not it's a constant.  So, I'm saving it as a variable that doesn't
# change.  In theory, hm... no idea whether this will give me speed-up or not.

import math
import numpy
import operator

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
  about the lower left triangle of values -- see program where i handle this 
  correctly. 
  """
  matrix = {}
  length = len(centroids)

  for i in xrange(0, length):
    matrix[i] = {}

    for j in xrange(i + 1, length):
      matrix[i][j] = similarity(centroids[i], centroids[j])

  return matrix

def getSimsFromMatrix(matrix):
  """
  Given a matrix of similarity values, covert to a straight list.
  """
  
  sims = []
  
  for i in matrix.keys():
    for j in matrix[i].keys():
      sims.append(matrix[i][j])
  
  return sims

def getSims(centroids):
  """
  Given a list of Centroids, compute the similarity score between all 
  pairs and return the list.  This can be fed into findAvg(), findStd().
  """

  sims = []
  length = len(centroids)
  
  for i in xrange(0, length):
    for j in xrange(i + 1, length):
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
  length = len(centroids)
  
  for i in xrange(0, length):
    for j in xrange(i + 1, length):
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

  length = len(centroids)

  for i in xrange(0, length):
    for j in xrange(i + 1, length):
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
  length = len(centroids)

  for i in xrange(0, length):
    for j in xrange(i + 1, length):
      curr_sim = similarity(centroids[i], centroids[j])
      if curr_sim > max_sim:
        max_sim = curr_sim
        max_i = i
        max_j = j

  return (max_i, max_j, max_sim)

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
  
  def topTerms(self, n):
    """
    Returns the n-highest tf-idf terms in the vector.
    
    n := the number of terms to get.
    """
  
    sorted_tokens = sorted(
                           self.centroidVector.items(),
                           key=operator.itemgetter(1), # (1) is value
                           reverse=True)
  
    #print "len(sorted_tokens): %d" % len(sorted_tokens)

    # count to index
    to_print = min(n, len(sorted_tokens))
    top_terms = []
  
    for i in xrange(0, to_print):
      top_terms.append(sorted_tokens[i])

    return top_terms

  def addCentroid(self, newCen):
    """
    This merges in the new centroid.
    
    newCent := the centroid object to add.
    """
    self.addVector(newCen.name, newCen.vectorCnt, newCen.centroidVector)

  def addVector(self, docName, addCnt, newDocVec):
    """
    This averages in the new vector.
    
    docName   := the name of the thing we're adding in.
    addCnt    := the number of documents represented by newV.
    newDocVec := the vector representing the document(s).
    
    This is copied and translated directly from my c# program.
    """
    
    # determine the weight of the merging pieces
    oldWeight = float(self.vectorCnt) / (self.vectorCnt + addCnt)
    newWeight = float(addCnt) / (self.vectorCnt + addCnt)
    
    if len(self.name) == 0:
      self.name = docName
    else:
      self.name += ", %s" % docName
    
    # computes magnitude as it goes.
    self.length = 0
    
    # reduce weight of values already in vector
    for key in self.centroidVector.keys():
      if key in newDocVec: # if is in both vectors!
        
        oldValue = float(self.centroidVector[key]) * oldWeight
        newValue = float(newDocVec[key]) * newWeight
        value = oldValue + newValue
        
        self.centroidVector[key] = value
        self.length += (value * value) # magnitude
                
        # so when we go through to add in all the missing ones we won't have 
        # excess
        del newDocVec[key]
      else: # if it is strictly in the old vector
        
        oldValue = float(self.centroidVector[key]) * oldWeight
        self.centroidVector[key] = oldValue
        self.length += (oldValue * oldValue) # magnitude
    
    # add new values to vector
    for key, value in newDocVec.iteritems():
      # we don't so we'll have to create a new value with the weight of the 
      # added vector
      value = float(value) * newWeight
      self.centroidVector[key] = value
      self.length += (value * value)

    self.vectorCnt += addCnt

    # calculate magnitude
    self.length = math.sqrt(self.length)
    
