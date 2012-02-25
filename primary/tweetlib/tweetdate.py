#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This handles the date string parsing my tweets use.
#

import re

months = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'}

weekdays = {
    'Mon': '00',
    'Tue': '01',
    'Wed': '02',
    'Thu': '03',
    'Fri': '04',
    'Sat': '05',
    'Sun': '06'}

def getMonthFromInt(dateVal):
  """
  Grab the year from a date integer, the first four digits.
  Input: YYYYMMHH...
  Output: MM or -1 on error
  """
  
  monre = re.search('^\d{4}(\d{2})', str(dateVal))
  if monre == None:
    return -1
  else:
    return int(monre.group(1))

def getYearFromInt(dateVal):
  """
  Grab the year from a date integer, the first four digits.
  Input: YYYYMMHH...
  Output: YYYY or 0 on error
  """
  
  yearre = re.search('^(\d{4})', str(dateVal))
  if yearre == None:
    return 0
  else:
    return int(yearre.group(1))

def getDayOfWeek(dateStr):
  """
  Get the day of the week from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: Fri (see above)
  """
  
  # ----------------Fri     Jan     21    09  : 28  :  12   +0000   2011
  day = re.search('(\w{3}) \w{3} \d{1,2} \d{2}:\d{2}:\d{2} \+\d{4} \d{4}', dateStr)
  
  if day:
    return day.group(1)
  
  return ""

def buildDateTimeInt(dateStr):
  """
  Build a date integer from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: YYYYMMDDHHMMSS
  """

  # ----------------Fri   Jan       21        09  : 28    :  12     +0000   2011
  # ----------------        1        2        3       4       5               6
  day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):(\d{2}):(\d{2}) \+\d{4} (\d{4})', dateStr)

  if day == None:
    print "regex doesn't match anything"
    date = -1
  else:
    date = int(day.group(6) + months[day.group(1)] + day.group(2) + day.group(3) + day.group(4) + day.group(5))

  return date

def buildDateInt(dateStr):
  """
  Build a date integer from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: YYYYMMDDHH
  """

  # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
  # ----------------        1        2        3                           4
  day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', dateStr)

  if day == None:
    print "regex doesn't match anything"
    date = -1
  else:
    date = int(day.group(4) + months[day.group(1)] + day.group(2) + day.group(3))

  return date

def buildDateDayInt(dateStr):
  """
  Build a date integer from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: YYYYMMDD
  """

  day = re.search('\w{3} (\w{3}) (\d{1,2}) \d{2}:\d{2}:\d{2} \+\d{4} (\d{4})', dateStr)

  if day == None:
    print "regex doesn't match anything"
    date = -1
  else:
    date = int(day.group(3) + months[day.group(1)] + day.group(2))

  return date

def buildDateMonthInt(dateStr):
  """
  Build a date integer from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: MM
  """

  # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
  # ----------------        1        2        3                           4
  day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', dateStr)

  if day == None:
    print "regex doesn't match anything"
    date = -1
  else:
    date = int(months[day.group(1)])

  return date

def buildDateYearInt(dateStr):
  """
  Build a date integer from the string.
  Input: Fri Jan 21 09:28:12 +0000 2011
  Output: YYYY
  """

  # ----------------Fri   Jan       21        09  : 28  :  12   +0000   2011
  # ----------------        1        2        3                           4
  day = re.search('\w{3} (\w{3}) (\d{1,2}) (\d{2}):\d{2}:\d{2} \+\d{4} (\d{4})', dateStr)

  if day == None:
    print "regex doesn't match anything"
    date = -1
  else:
    date = int(day.group(4))

  return date

class TweetTime:
  """
  Stores the datetime string in pieces.
  """
  def __init__(self, timedate=""):
    """
    Input:
      timedate := "Fri Jan 21 09:28:12 +0000 2011"
    """
    self.strrep = timedate
    self.weekdayVal = 0
    self.weekdayStr = ""
    self.monthStr = ""
    self.monthVal = 0
    self.monthDayVal = 0
    self.hour = 0
    self.minute = 0
    self.second = 0
    self.year = 0
    self.valid = False

    # ----------------Fri     Jan       21        09  : 28  :  12      +0000    2011
    # ---------------- 1        2        3         4     5      6                7
    day = re.search('(\w{3}) (\w{3}) (\d{1,2}) (\d{2}):(\d{2}):(\d{2}) \+\d{4} (\d{4})', timedate)
    
    if day == None:
      print "regex fails"
    else:
      self.valid = True
      self.weekdayStr = day.group(1)
      self.weekdayVal = weekdays[day.group(1)]
      self.monthStr = day.group(2)
      self.monthVal = months[day.group(2)]
      self.monthDayVal = int(day.group(3))
      self.hour = int(day.group(4))
      self.minute = int(day.group(5))
      self.second = int(day.group(6))
      self.year = int(day.group(7))

  def __str__(self):
    return self.strrep
      
    
