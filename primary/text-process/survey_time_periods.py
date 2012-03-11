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
    usersperday = {}
    tweetspermonth = {} # this is used to track
    dates = {} # this will be a set() of days per month
    oldest = 20991231
    newest = 19990101

    start = time.clock()

    # XXX: This doesn't yet do what I want.
    for row in conn.cursor().execute(query % (minimum, maximum)):
        uid = row['owner']

        if row['created'] is not None:
            twt = tweetdate.TweetTime(row['created'])

            year = twt.year
            month = twt.month_val
            day = twt.monthday_val
            data = twt.yearmonday

            # Determining which months have a tweet for each day.
            try:
                dates[year][month].add(day)
            except KeyError:
                try:
                    dates[year][month] = set()
                    dates[year][month].add(day)
                except KeyError:
                    dates[year] = {}
                    dates[year][month] = set()
                    dates[year][month].add(day)
            
            # How many tweets I collected for that day.
            try:
                tweetspermonth[year][month] += 1
            except KeyError:
                try:
                    tweetspermonth[year][month] = 1
                except KeyError:
                    tweetspermonth[year] = {}
                    tweetspermonth[year][month] = 1

            # How many users tweeted that day.
            try:
                usersperday[year][month].add(uid)
            except KeyError:
                try:
                    usersperday[year][month] = set()
                    usersperday[year][month].add(uid)
                except KeyError:
                    usersperday[year] = {}
                    usersperday[year][month] = set()
                    usersperday[year][month].add(uid)

            if data < oldest:
                oldest = data
            if data > newest:
                newest = data

    conn.close()

    print "query time: %fm" % ((time.clock() - start) / 60)
    
    # -------------------------------------------------------------------------
    # Build a matrix.  Which dates have the most users.
    #

    # -------------------------------------------------------------------------
    # Search the dates stored and identify which months have tweets on each 
    # day.
    #
    # Do we have any full months?
    #
    full_dates = {}
    
    for year in dates:
        for month in dates[year]:
            num_days = calendar.monthrange(year, int(month))
            if num_days[1] == len(dates[year][month]):
                full_dates["%4d%02d" % (year, month)] = (tweetspermonth[year][month], usersperday[year][month])

    start_year = tweetdate.get_yearfromint(oldest)
    start_month = tweetdate.get_monthfromint(oldest)

    end_year = tweetdate.get_yearfromint(newest)
    end_month = tweetdate.get_monthfromint(newest)

    print "start:end :: %4d%02d:%4d%02d" % (start_year, start_month, end_year, end_month)
    for date in sorted(full_dates):
        # guaranteed that there will be an entry as full_dates are a subset.
        print "%s:%s" % (date, full_dates[date])

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
