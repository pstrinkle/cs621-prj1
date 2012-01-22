#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This handles representing/storing document centroids in a vector space model.
#

class Centroid:
  """
  This data structure represents an average of documents in a vector space.
  
  Amusingly, modeled directly after a C# class I wrote for a class I took.
  """
  
  def __init__(self):
    """
    No parameters required -- fancy stuff here, lol.
    """
    self.name = ""
    self.vectorCnt = 0
    self.vector = {}
    self.length = 0.00
    

  def __len__(self):
    """
    Get the length of it!
    """
    return len(self.vector)

  def addVector(self, name, addCnt, newV):
    """
    This averages in the new vector.
    
    name   := the name of the thing we're adding in.
    addCnt := the number of documents represented by newV.
    newV   := the vector representing the document(s).
    """
    
    
