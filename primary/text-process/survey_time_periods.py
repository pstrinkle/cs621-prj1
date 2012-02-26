#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author Patrick Trinkle
# Summer 2011
# Spring 2012
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

    query_collect = "select owner from tweets group by owner having count(*) >= %d and count(*) < %d"
    query_prefetch = "select owner, created from tweets where owner in (%s);"

    query = query_prefetch % query_collect

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    # -------------------------------------------------------------------------
    # Search the database file for users.
    users = []
    dates = {}
    oldest = 20991231
    newest = 19990101

    start = time.clock()

    # XXX: This doesn't yet do what I want.
    for row in conn.cursor().execute(query % (minimum, maximum)):
        #uid = row['owner']
        #if uid not in users:
            #users.append(uid)

        if row['created'] is not None:
            twt = tweetdate.TweetTime(row['created'])

            year = twt.year
            month = twt.month_val
            data = twt.yearmonday
            
            print data
            
            # amusing. I know.
            try:
                dates[year][month] += 1
            except KeyError:
                try:
                    dates[year][month] = 1
                except KeyError:
                    dates[year] = {}
                    dates[year][month] = 1

            if data < oldest:
                oldest = data
            if data > newest:
                newest = data

    conn.close()

    print "query time: %fm" % ((time.clock() - start) / 60)

    # So, I could get the distinct, max, and min from the sql query itself; and
    # the counts... lol
    full_dates = []

    # For which months in which years do I have tweets from every day -- 
    # possibly all from one user, so not the most useful information -- but 
    # still.
    for year in dates:
        for month in dates[year]:
            num_days = calendar.monthrange(year, int(month))
            if num_days == dates[year][month]:
                full_dates.append("%s%s" % (str(year), str(month)))

    start_year = tweetdate.get_yearfromint(oldest)
    start_month = tweetdate.get_monthfromint(oldest)

    end_year = tweetdate.get_yearfromint(newest)
    end_month = tweetdate.get_monthfromint(newest)

    print "users: %d\n" % len(users)
    print "start: %4d%2d:%4d%2d" % (start_year, start_month, end_year, end_month)
    print "full_dates: %s" % str(full_dates)
    #for uid in dates:
        #print dates[uid]

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
