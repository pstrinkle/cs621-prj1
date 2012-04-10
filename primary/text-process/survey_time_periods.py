#! /usr/bin/python
"""Given a database of tweets, identify the best months for further 
experiments."""

__author__ = 'tri1@umbc.edu'

##
# @author Patrick Trinkle
# Spring 2012
#
# @summary: The goal of this program is to identify good months in my data set
# for use in other experiments.
#

import os
import sys
import time
import sqlite3
import calendar
import operator

sys.path.append(os.path.join("..", "tweetlib"))
import tweetdate

def compare(set_a, set_b):
    """Compare two sets of users, return number of in common."""
        
    cnt = 0
        
    for user in set_a:
        if user in set_b:
            cnt += 1
    
    return cnt

class DateSurvey():
    """Data structure for storing survey information."""

    def __init__(self):
        self.dates = {} # this will be a set() of days per month
        self.tweetspermonth = {} # this is used to track
        self.usersperday = {}
        self.full_dates = {}
        # how many users were in common between key'd months
        self.usermonths = {}
        self.computed_full = False
        self.computed_similar = False
        self.oldest = 20991231
        self.newest = 19990101
    
    def get_dates(self):
        """Get raw date structure."""
        
        return self.dates
    
    def get_full(self):
        """Get full dates set."""
        
        if self.computed_full is False:
            self.compute_full()

        return self.full_dates

    def get_similar(self):
        """Get similar dates."""
        
        if self.computed_similar is False:
            self.compute_similar()
        
        return self.usermonths
    
    def compute_full(self):
        """Determine which months have at least one tweet per day for a month.
        """
        
        for year in self.dates:
            for month in self.dates[year]:
                num_days = calendar.monthrange(year, int(month))
                if num_days[1] == len(self.dates[year][month]):
                    yrmt = "%4d%02d" % (year, month)
                    self.full_dates[yrmt] = \
                        (self.tweetspermonth[yrmt], self.usersperday[yrmt])
    
    def add_date(self, year, month, day):
        """Add a date to the set of survey data."""
        
        try:
            self.dates[year][month].add(day)
        except KeyError:
            try:
                self.dates[year][month] = set()
                self.dates[year][month].add(day)
            except KeyError:
                self.dates[year] = {}
                self.dates[year][month] = set()
                self.dates[year][month].add(day)
        
        # How many tweets I collected for that day.
        try:
            self.tweetspermonth["%4d%02d" % (year, month)] += 1
        except KeyError:
            self.tweetspermonth["%4d%02d" % (year, month)] = 1

    def compute_similar(self):
        """Determine which dates have the most users in common."""
        
        length = len(self.usersperday)
        months = self.usersperday.keys()
        
        for i in xrange(0, length):
            for j in xrange(i + 1, length):
                self.usermonths["%s:%s" % (months[i], months[j])] = \
                    compare(
                            self.usersperday[months[i]],
                            self.usersperday[months[j]]) 

    def add_user(self, year, month, uid):
        """How many users tweeted that day."""
        
        try:
            self.usersperday["%4d%02d" % (year, month)].add(uid)
        except KeyError:
            self.usersperday["%4d%02d" % (year, month)] = set()
            self.usersperday["%4d%02d" % (year, month)].add(uid)

def data_pull(database_file, query):
    """Pull the data from the database."""
    
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    # -------------------------------------------------------------------------
    # Search the database file for users.
    survey = DateSurvey()

    for row in conn.cursor().execute(query):
        uid = row['owner']

        if row['created'] is not None:
            twt = tweetdate.TweetTime(row['created'])

            year = twt.year
            month = twt.get_month()["val"]
            day = twt.get_month()["day_val"]
            data = twt.yearmonday

            # Determining which months have a tweet for each day.
            survey.add_date(year, month, day)
            survey.add_user(year, month, uid)

            if data < survey.oldest:
                survey.oldest = data
            if data > survey.newest:
                survey.newest = data

    conn.close()
    
    return

def usage():
    """Usage"""

    print "%s <database_file> <minimum> <maximum> <output>" % sys.argv[0]
    print "\t>= minimum"
    print "\t< maximum"

def main():
    """Entry point."""

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

    start = time.clock()

    survey = data_pull(database_file, query % (minimum, maximum))

    print "query time: %fm" % ((time.clock() - start) / 60)

    # -------------------------------------------------------------------------
    # Search the dates stored and identify which months have tweets on each 
    # day.
    #
    # Do we have any full months?
    #
    full_dates = survey.get_full()
    incommon = survey.get_similar()

    sorted_incommon = sorted(
                             incommon.items(),
                             key=operator.itemgetter(1), # (1) is value
                             reverse=True)

    start_year = tweetdate.get_yearfromint(survey.oldest)
    start_month = tweetdate.get_monthfromint(survey.oldest)

    end_year = tweetdate.get_yearfromint(survey.newest)
    end_month = tweetdate.get_monthfromint(survey.newest)

    print "building output"

    with open(output_file, "w") as fout:
        fout.write("data:\n")
        fout.write("start:end :: %4d%02d:%4d%02d\n" % \
            (start_year, start_month, end_year, end_month))

        fout.write("months w/ a tweet collected from each day (at least one)\n")
        for date in sorted(full_dates):
            fout.write("%s:%s\n" % (date, full_dates[date]))

        fout.write("number in common\n")
        for com in sorted_incommon:
            fout.write("%s\n" % com)

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
