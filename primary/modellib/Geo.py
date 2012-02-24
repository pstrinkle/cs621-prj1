#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This handles the Earth coordinate stuff.
#
# Currently implemented to only support the degree decimal system.

import math

def kms_to_smi(kilos_squared):
  """
  Given an area in kilometers squared, calculate the square mileage.
  
  1 (kilometer squared) = 0.386102159 square miles
  
  Input: kilos_squared := area
  
  Returns: square miles
  """
  return kilos_squared * 0.386102159

def km_to_mi(kilos):
  """
  Given a distance in kilometers, calculate the mileage.
  
  1 kilometer = 0.621371192 miles
  
  Input: kilos := distance
  
  Returns: miles
  """
  return kilos * 0.621371192

def haversin(theta):
  """
  Given a theta, return the haversin value.
  
  See: http://en.wikipedia.org/wiki/Haversine_formula
  
  Input: theta := angle in radians
  
  Return: haversin(theta)
  """
  h = math.sin(theta / 2) * math.sin(theta / 2)
  
  return h

def calculate_distance(coordA, coordB):
  """
  Given two points on Earth, calculate the distance between them in kilometers.

  haversin(rad) = sin**2(rad * 0.5) = (1-cos(rad)) * 0.5
  haversin(d / R) = haversin(lat2 - lat1) + cos(lat1)cos(lat2)haversin(lon2-lon1)
  h = haversin(d / R)
  d = 2*R*arcsin(sqrt(h)
  
  h = haversin(lat2 - lat1) + cos(lat1)cos(lat2)haversin(lon2-lon1)
  d = 2*R*arcsin(sqrt(h)
  
  Input: coordA := point A as a coordinate tuple [lat, long]
         coordB := point B as a coordinate tuple
  
  Return: floating point value distance between points on Earth.
  """
  
  if len(coordA) != 2 or len(coordB) != 2:
    return 0
  
  lat1, long1 = coordA
  lat2, long2 = coordB
  
  dynlat = math.radians(lat2 - lat1)
  dynlong = math.radians(long2 - long1)
  
  rlat1 = math.radians(lat1)
  rlat2 = math.radians(lat2)

  # radius of Earth in kilometers
  radius = 6371
  
  h = haversin(dynlat) + (math.cos(rlat1) * math.cos(rlat2) * haversin(dynlong))
  
  d = 2 * radius * math.asin(math.sqrt(h))
  
  return d

def calculate_area(box, lat=0, long=1):
  """
  Given a rectangle of GPS coordinates in the Twitter format used with all
  other box functions.  Calculate the area in square kilometers.
  
  Input: box  := rectangle for area calculation.
         lat  := index of the latitude value within a coordinate
         long := index of the longitude value within a coordinate
  
  Return: area in square kilometers.
  """

  #print "%f,%f  --- %f,%f  " % (upper_left[1], upper_left[0], upper_right[1], upper_right[0])
  #print "|              |  "
  #print "%f,%f  --- %f,%f  " % (lower_left[1], lower_left[0], lower_right[1], lower_right[0])
  
  lower_left = box[0]
  lower_right = box[1]
  upper_right = box[2]
  upper_left = box[3]
  
  vert = calculate_distance((upper_left[lat], upper_left[long]), (lower_left[lat], lower_left[long]))
  horz = calculate_distance((upper_left[lat], upper_left[long]), (upper_right[lat], upper_right[long]))
  
  return vert * horz

def merge_box(boxA, boxB, lat=0, long=1):
  """
  Given two rectangles of Twitter GPS coordinates, merge the boxes into the encompassing
  rectangle.
  
  Input: boxA := rectangle of GPS coordinates.
         boxB := rectangle of GPS coordinates.
         lat  := index of the latitude value within a coordinate
         long := index of the longitude value within a coordinate
  
  Return: Encompassing box.
  """
  
  if len(boxA) != 4 or len(boxB) != 4:
    return None
  
  lower_leftA = boxA[0]
  lower_rightA = boxA[1]
  upper_rightA = boxA[2]
  upper_leftA = boxA[3]

  lower_leftB = boxB[0]
  lower_rightB = boxB[1]
  upper_rightB = boxB[2]
  upper_leftB = boxB[3]
  
  maxlat = upper_leftA[lat]
  minlat = lower_leftA[lat]
  left_long = upper_leftA[long]
  right_long = upper_rightA[long]
  
  if maxlat < upper_leftB[lat]:
    maxlat = upper_leftB[lat]

  if minlat > lower_leftB[lat]:
    minlat = lower_leftB[lat]
  
  if left_long > upper_leftB[long]:
    left_long = upper_leftB[long]
  
  if right_long < upper_rightB[long]:
    right_long = upper_rightB[long]
  
  # long, lat
  lower_left = [left_long, minlat]
  lower_right = [right_long, minlat]
  upper_right = [right_long, maxlat]
  upper_left = [left_long, maxlat]
  
  #print "box a:"
  #print "%f,%f  --- %f,%f  " % (upper_leftA[lat], upper_leftA[long], upper_rightA[lat], upper_rightA[long])
  #print "|              |  "
  #print "%f,%f  --- %f,%f  " % (lower_leftA[lat], lower_leftA[long], lower_rightA[lat], lower_rightA[long])
  
  #print "box b:"
  #print "%f,%f  --- %f,%f  " % (upper_leftB[lat], upper_leftB[long], upper_rightB[lat], upper_rightB[long])
  #print "|              |  "
  #print "%f,%f  --- %f,%f  " % (lower_leftB[lat], lower_leftB[long], lower_rightB[lat], lower_rightB[long])
  
  #print "merged:"
  #print "%f,%f  --- %f,%f  " % (upper_left[lat], upper_left[long], upper_right[lat], upper_right[long])
  #print "|              |  "
  #print "%f,%f  --- %f,%f  " % (lower_left[lat], lower_left[long], lower_right[lat], lower_right[long])
    
  return lower_left, lower_right, upper_right, upper_left

def within_box(box, point):
  """
  Given a bounding box on Earth, determine whether the specified point is within the box.
  
  Twitter weirdly stores the place coordinates in [long, lat]
  
  [[[-121.794055, 38.534883], [-121.675465, 38.534883],
    [-121.675465, 38.578737], [-121.794055, 38.578737]]]

  38.546354, -121.758611
  
  Input: box := four point box describing a piece of Earth [weird format]:
         [long, lat], [long, lat], (lower_left, lower_right),
         [long, lat], [long, lat]  (upper_right, upper_left)
         point := a coordinate tuple [lat, long]
  
  Return: True if the point is within the box; False otherwise.
  """
  
  if len(box) != 4 or len(point) != 2:
    return False
  
  # These are long, lat
  lower_left = box[0]
  lower_right = box[1]
  upper_right = box[2]
  upper_left = box[3]
  
  # These are lat, long
  lat = point[0]
  longitude = point[1]
  
  #print "%f,%f  --- %f,%f  " % (upper_left[1], upper_left[0], upper_right[1], upper_right[0])
  #print "|              |  "
  #print "%f,%f  --- %f,%f  " % (lower_left[1], lower_left[0], lower_right[1], lower_right[0])
  
  if lat > upper_left[1] or lat < lower_left[1]:
    return False
  
  if longitude > upper_right[0] or longitude < upper_left[0]:
    return False
  
  return True
