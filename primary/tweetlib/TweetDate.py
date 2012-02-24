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
  
