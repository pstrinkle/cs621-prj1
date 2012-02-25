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

def findStd(centroids, short_cut=False, sim_scores=None):
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

def findAvg(centroids, short_cut=False, sim_scores=None):
  """
  Given a list of Centroids, compute the similarity of each pairing and return 
  the average.
  
  If short_cut is True, it'll use sim_scores as the input instead of calculating
   the scores.
  
  This can only work on the early perfect version of the centroid list.
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

  def __str__(self):
    """
    Get the string representation.  In this case, it's the name and the top 10
    terms.
    """

    output = "%s:\n%s" % (self.name, self.topTerms(10))

    return output

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

def findMatrixMax(matrix):
  """
  This provides the outer and inner key and the value, of the maximum value.
  """

  max_val = 0.0
  max_i = 0
  max_j = 0

  for i in matrix.keys():
    try:
      kvp = max(matrix[i].iteritems(), key=operator.itemgetter(1))
    except ValueError:
      continue
    
    # Maybe I should store the max value with the array, and then always store
    # the previous largest, and when i insert or delete...
    
    if kvp[1] > max_val:
      max_val = kvp[1]
      max_i = i
      max_j = kvp[0]

  return (max_i, max_j, max_val)

def removeMatrixEntry(matrix, key):
  """
  This removes any matrix key entries, outer and inner.
  """

  try:
    del matrix[key]
  except KeyError:
    print "deleting matrix[%s]" % str(key)
    print "%s" % matrix.keys()
    raise Exception

  for i in matrix.keys():
    try:
      del matrix[i][key]
    except KeyError:
      continue

def addMatrixEntry(matrix, centroids, new_centroid, name):
  """
  Add this entry and comparisons to the matrix, the key to use is name.
  
  Really just need to matrix[name] = {}, then for i in matrix.keys() where not
  name, compare and add.
  
  Please remove before you add, otherwise there can be noise in the data.
  """

  if name in matrix:
    print "enabling matrix[%s] <-- already there!" % str(name)

  matrix[name] = {}

  for i in matrix.keys():
    if i != name:
      matrix[name][i] = Centroid.similarity(centroids[i], new_centroid)

def clusterDocuments(documents, thresholdStr="std"):
  """
  Given a dictionary of documents, where the key is some unique (preferably)
  id value.  Create a centroid representation of each, and then merge the
  centroids by their similarity scores.
  
  documents := dictionary of documents in tf-idf vectors.
  thresholdStr := either "std" or "avg" to set the threshold.
  """
  
  centroids = {}
  arbitrary_name = 0

  for doc, vec in documents.iteritems():
    centroids[arbitrary_name] = Centroid.Centroid(str(doc), vec) 
    arbitrary_name += 1

  # The size of sim_matrix is: (num_centroids^2 / 2) - (num_centroids / 2)
  # -- verified, my code does this correctly. : )

  sim_matrix = Centroid.getSimMatrix(centroids)
  initial_similarities = Centroid.getSimsFromMatrix(sim_matrix)
  
  if thresholdStr == "std":
    threshold = Centroid.findStd(centroids, True, initial_similarities)
  elif thresholdStr == "avg":
    threshold = Centroid.findAvg(centroids, True, initial_similarities)
  else:
    return None

  # -------------------------------------------------------------------------
  # Merge centroids
  while len(centroids) > 1:
    i, j, sim = findMatrixMax(sim_matrix)

    if sim >= threshold:
        
      centroids[i].addCentroid(centroids[j])
      del centroids[j]

      removeMatrixEntry(sim_matrix, i)
      removeMatrixEntry(sim_matrix, j)
      addMatrixEntry(sim_matrix, centroids, centroids[i], i)
    else:
      break
  
  return centroids
