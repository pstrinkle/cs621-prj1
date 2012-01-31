#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles representing/storing document centroids in a vector space model.
#

import math

class Centroid:
  """
  This data structure represents an average of documents in a vector space.
  
  Amusingly, modeled directly after a C# class I wrote for a class I took.
  """
  
  def __init__(self, name):
    """
    Representation of a document(s) as a tf-idf vector.
    
    name the name for it.
    """
    self.name = name
    self.vectorCnt = 0
    self.centroidVector = {}
    self.length = 0.00
    

  def __len__(self):
    """
    Get the length of it!
    """
    return len(self.vector)

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
    centroidTerms = list(this.centroidVector.keys())
    
    # reduce weight of values already in vector
    for key in centroidTerms:
      if key in newDocVec: # if is in both vectors!
        oldValue = float(self.centroidVector[key]) * oldWeight
        newValue = float(newDocVec[key]) * newWeight
        
        self.centroidVector[key] = oldValue + newValue
        
        # so when we go through to add in all the missing ones we won't have excess
        newDocVec.remove(key)
      else: # if it is strictly in the old vector
        oldValue = float(self.centroidVector[key]) * oldWeight
        self.centroidVector[key] = oldValue
    
    # add new values to vector
    for key, value in newDocVec:
      # we don't so we'll have to create a new value with the weight of the added vector
      newValue = value * newWeight
      self.centroidVector.add(key, newValue)

    self.vectorCnt += addCnt
    self.length = 0
    
    # calculate magnitude
    for key, value in self.centoidVector:
      self.length += (value * value)
    
    self.length = math.sqrt(self.length)

    
    
