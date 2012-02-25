#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This handles the geo-graphic model stuff.
#
# TODO: unfinished.
# Currently somewhat stupidly handled.

import re
import os
import sys
import geo as g

sys.path.append(os.path.join("..", "tweetlib"))
import tweetdate as td

class LocationBundle:
  """
  This object assigns geo-graphic coordinates to date time occurrences.
  
  This should eventually take the geo-coordinate and obtain the timezone and 
  adjust the tweet time appropriately.
  
  days['dayofweek'] has a dictionary of timestamps (YYYYMMDDHH) and coordinates (coords in a list)
  
  So we can identify where they are on Mondays, over a period of time, etc. 
  """
  
  weekDays = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
  yearMonths = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
  
  def __init__(self):
    """
    No parameters required -- fancy stuff here, lol.
    """
    self.count = 0
    self.days = {}
    self.days['Mon'] = {}
    self.days['Tue'] = {}
    self.days['Wed'] = {}
    self.days['Thu'] = {}
    self.days['Fri'] = {}
    self.days['Sat'] = {}
    self.days['Sun'] = {}
    self.locations = {}
    self.centroid = [0, 0]
    self.centroided = False

  def __len__(self):
    """
    How many occurrences of coordinates we have encountered.
    
    Call len(x.locations) for distinct count.
    """
    return self.count

  def add_tweet(self, time_string, coord_string):
    """
    time_string := Fri Jan 21 09:28:12 +0000 2011
    coord_string := lat, long
    """
    dow = td.getDayOfWeek(time_string)
    ymdh = td.buildDateInt(time_string)
    
    coord = re.search("(.+),(.+)", coord_string)
    
    if coord:
      latlong = [float(coord.group(1)), float(coord.group(2))]
      #print "dow: %s ymdh: %d geo: %s" % (dow, ymdh, latlong)
      
      if ymdh not in self.days[dow]:
        self.days[dow][ymdh] = []

      self.days[dow][ymdh].append(latlong)
      self.count += 1
      
      try:
        self.locations[str(latlong)] += 1
      except KeyError:
        self.locations[str(latlong)] = 1

      #print self.days
    
  def dump_timeplace(self):
    """
    Dumps the time and place information.
    
    --- Okay, I'm not certain about how useful this will be.
    """
    
    for day in self.weekDays:
      events = self.days[day].keys()
      events.sort()
      
      print "%s" % day
      for event in events:
        print "%d: %s" % (event, self.days[day][event])

  def dump_weekdayhourly3d(self):
    """
    Each data set in the output file represents a line in 3d, where its position
    on the z axis is the day of the week.
    """
    
    out = "# hour count (each set is a day, sun, mon, tue, ...)\n"
    out += "# should add to %d\n" % self.count

    data = {} # 'Mon', 'Tue', 'Wed', ...
    
    for day in self.weekDays:
      data[day] = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0,
                   6:0, 7:0, 8:0, 9:0, 10:0, 11:0,
                  12:0, 13:0, 14:0, 15:0, 16:0, 17:0,
                  18:0, 19:0, 20:0, 21:0, 22:0, 23:0}
      
      # for each event within the weekday
      # events are int's YYYYMMDDHH, self.days[day][event] is an array of latlongs.
      for event in self.days[day].keys():
        m = re.search("\d{4}\d{2}\d{2}(\d{2})", str(event))
        if m:
          hour = int(m.group(1))
          
          try:  
            data[day][hour] += len(self.days[day][event])
          except KeyError:
            data[day][hour] = len(self.days[day][event])

    # build output string
    # I can actually do this while building up data{}{}..., but let's get it working before
    # optimizing.
    out += "# x y z"
    out += "# hour dayindx count\n"
    for i in range(len(self.weekDays)):
      day = self.weekDays[i]
      
      for hour in data[day]:
        out += "%d %d %d\n" % (hour, i, data[day][hour])
      out += "\n" # extra to space sets apart.

    return out

  def dump_weekdayhourly(self):
    """
    """
    
    out = "# hour count (each set is a day, sun, mon, tue, ...)\n"
    out += "# should add to %d\n" % self.count

    data = {} # 'Sun', 'Mon', 'Tue', ...
    
    for day in self.weekDays:
      data[day] = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0,
                   6:0, 7:0, 8:0, 9:0, 10:0, 11:0,
                  12:0, 13:0, 14:0, 15:0, 16:0, 17:0,
                  18:0, 19:0, 20:0, 21:0, 22:0, 23:0}
      
      # for each event within the weekday
      # events are int's YYYYMMDDHH, self.days[day][event] is an array of latlongs.
      for event in self.days[day].keys():
        m = re.search("\d{4}\d{2}\d{2}(\d{2})", str(event))
        if m:
          hour = int(m.group(1))
          
          try:  
            data[day][hour] += len(self.days[day][event])
          except KeyError:
            data[day][hour] = len(self.days[day][event])

    # build output string
    for hour in data[self.weekDays[0]]:
      out += "%d " % hour
      for day in self.weekDays:
        out += "%d " % (data[day][hour])
      out += "\n"

    return out
  
  def dump_latlong_count(self, normalize=0.0):
    """
    Dumps the Long,Lat,Count for using with gnuplot.  This doesn't yet filter by year or month.
    
    Input: normalize, added to both latitude and longitude.
    Output := a string. : )
    
    This does what I want.
    """
    
    out = "# longitude lat count\n"
    
    for loc in self.locations:
      m = re.search("\[(.+?),(.+?)\]", loc)
      if m:
        lat = float(m.group(1)) + normalize
        longitude = float(m.group(2)) + normalize
        cnt = self.locations[loc]
        out += "%f %f %d\n" % (longitude, lat, cnt)

    return out

  def by_year_data(self, year=0):
    """
    Attempts to dump the time and place information, well just time and occurrence count.
    
    --- Okay, I'm not certain about how useful this will be.
    """

    # ymdh
    eventsForYear = {}
    
    min_ymdh = int("%d000000" % year)
    max_ymdh = int("%d000000" % (year + 1))
    
    for day in self.days:
      for event in self.days[day]:
        if event >= min_ymdh or event < max_ymdh:
          eventsForYear[event] = []
          for item in self.days[day][event]:
            eventsForYear[event].append(item)
  
  def dump_centroiddistance_occurrence(self, sort_output=False):
    """
    The x-axis is distance from centroid (origin).
    The y-axis is the # occurrences.
    """
    
    if self.centroided == False:
      self.build_centroid()
      self.centroided = True
    
    out = "# dist count\n"
    
    if sort_output == True:
      data = {}
    
    for loc in self.locations:
      m = re.search("\[(.+?),(.+?)\]", loc)
      if m:
        lat = float(m.group(1))
        longitude = float(m.group(2))
        cnt = self.locations[loc]
        
        dist = g.calculate_distance(self.centroid, [lat, longitude])
        
        if sort_output == True:
          # the distances should be unique, because the points are...
          data["%f" % dist] = cnt
        else:
          out += "%f %d\n" % (dist, cnt)
    
    if sort_output == True:
      dpoints = data.keys()
      dpoints.sort() # sorts as a string, : (
      
      for p in dpoints:
        out += "%s %d\n" % (p, data[p])
    
    return out
  
  def average_distance(self):
    """
    Calculate the average distance between all pairs of coordinates (where i != j) --> (km, mi)
    """
    total = 0.0
    count = 0
    llocals = []
    
    # for each weekday
    for day in self.days:
      # for each timestamp for that day
      for timestamp in self.days[day]:
        # for each location for that timestamp
        for local in self.days[day][timestamp]:
          llocals.append(local)
    
    for i in range(len(llocals)):
      for j in range(len(llocals)):
        if i != j:
          dist = g.calculate_distance(llocals[i], llocals[j])
          total += dist
          count += 1
    
    if count == 0:
      return (0.0, 0.0)

    avg = total / count

    return (avg, g.km_to_mi(avg))
  
  def maximum_distance(self):
    """
    Calculate the maximum distance between all pairs of coordinates --> (km, mi)
    """
    maxVal = 0.0
    llocals = []
    
    # for each weekday
    for day in self.days:
      # for each timestamp for that day
      for timestamp in self.days[day]:
        # for each location for that timestamp
        for local in self.days[day][timestamp]:
          llocals.append(local)
    
    for i in range(len(llocals)):
      for j in range(len(llocals)):
        if i != j:
          dist = g.calculate_distance(llocals[i], llocals[j])
          #print "%s -> %s: %.2fmi" % (llocals[i], llocals[j], g.km_to_mi(dist))
          if dist > maxVal:
            maxVal = dist
    
    #print llocals
    #print "maximum distance: %f.2km (%.2fmi)" % (maxVal, g.km_to_mi(maxVal))
    
    return (maxVal, g.km_to_mi(maxVal))

  def build_centroid(self):
    """
    This builds the centroid for all their locations.
    """
    
    sumVal = 0
    pos = [0.0, 0.0]
    
    for loc in self.locations:
      m = re.search("\[(.+?),(.+?)\]", loc)
      if m:
        lat = float(m.group(1))
        longitude = float(m.group(2))
        cnt = self.locations[loc]
        
        pos[0] += cnt * lat
        pos[1] += cnt * longitude
        sumVal += cnt
    
    self.centroid[0] = pos[0] / sumVal
    self.centroid[1] = pos[1] / sumVal
    
    self.centroided = True

  def build_centroids(self):
    """
    Return an array of centroids
    
    TODO: Implement this.  Thing is, it really should take a parameter on how close two things have to be
    to draw a line.
    """
    
    return None