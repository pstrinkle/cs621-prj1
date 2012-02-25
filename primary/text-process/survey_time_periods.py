#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author Patrick Trinkle
# Spring 2011/Summer 2011
#
# @summary: The goal of this simple script is to run various queries against 
# Twitter through the published API, using the python-twitter open source 
# library.
#

import os
import sys
import time
import sqlite3
import calendar

sys.path.append(os.path.join("..", "tweetlib"))
import tweetdate

def usage():
  print "%s <database_file> <minimum> <maximum> <output>" % sys.argv[0]

def main():

  if len(sys.argv) != 5:
    usage()
    sys.exit(-1)
  
  database_file = sys.argv[1]
  minimum = int(sys.argv[2])
  maximum = int(sys.argv[3])
  output_file = sys.argv[4]

  # this won't return the 3 columns we care about.
  query_collect = \
    "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
  # "select id, contents as text from tweets where owner = %d;"
  query_prefetch = \
    "select owner, created from tweets where owner in (%s);"

  query = query_prefetch % query_collect

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()
  
  # ---------------------------------------------------------------------------
  # Search the database file for users.
  users = []
  dates = set()
  oldest = 20991231
  newest = 19990101

  start = time.clock()

  # XXX: This doesn't yet do what I want.
  for row in c.execute(query % (minimum, maximum)):
    uid = row['owner']
    if uid not in users:
      users.append(uid)

    if row['created'] is not None:
      data = tweetdate.buildDateDayInt(row['created'])
      dates.add(data)
      
      if data < oldest:
        oldest = data
      if data > newest:
        newest = data
  
  conn.close()

  print "query time: %fm" % ((time.clock() - start) / 60)

  # So, I could get the distinct, max, and min from the sql query itself; and
  # the counts... lol
  # calendar.monthrange(2009, 02)
  
  startYear = tweetdate.getYearFromInt(oldest)
  startMonth = tweetdate.getMonthFromInt(oldest)

  endYear = tweetdate.getYearFromInt(newest)
  endMonth = tweetdate.getMonthFromInt(newest)

  print "users: %d\n" % len(users)
  print "start: %s%s:%s%s" % (startYear, startMonth, endYear, endMonth)
  #for uid in dates:
    #print dates[uid]

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
