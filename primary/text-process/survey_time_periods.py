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

sys.path.append(os.path.join("..", "tweetlib"))
import TweetDate

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
  query_prefect = \
    "select owner, created from tweets where owner in (%s);"

  conn = sqlite3.connect(database_file)
  conn.row_factory = sqlite3.Row

  c = conn.cursor()
  
  # ---------------------------------------------------------------------------
  # Search the database file for users.
  users = []
  dates = {}

  start = time.clock()

  query = query_prefect % query_collect

  for row in c.execute(query % (minimum, maximum)):
    uid = row['owner']
    if uid not in users:
      users.append(uid)
    if row['created'] is not None:
      data = TweetDate.buildDateDayInt(row['created'])
      
      try:
        dates[uid].apend(data)
      except KeyError:
        dates[uid] = []
        dates[uid].apend(data)

  print "query time: %fm" % ((time.clock() - start) / 60)
  print "users: %d\n" % len(users)
  print dates
  
  conn.close()

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()