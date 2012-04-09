#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

##
# @author: Patrick Trinkle
# Spring 2012
#
# @summary: This program builds a tf-idf matrix for each day of a given YYYYMM.
#
# Currently it builds a list of users from that time period and only includes
# those that appear in each day...
#
# Use a full_date entry that also has a high user similarity count.
#
# 201107 works with the data set I have at present.
#
# select * from tweets where created like '%Jul%2011%';
#
# So yeah... just build tf-idf matrix for entire dictionary for the month.
# --- or maybe find the top terms for the month..?
#

import os
import sys
import sqlite3
import calendar
import operator
from ConfigParser import SafeConfigParser

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean
import tweetdate

sys.path.append(os.path.join("..", "modellib"))
import frame
import vectorspace
import imageoutput

class Output():
    """This holds the run parameters."""
    
    def __init__(self, output_folder, request_value):
        self.output_folder = output_folder # where to store everything
        self.request_value = request_value # the overall terms to pull daily
        self.overall_terms = [] # the terms overall for the month
        self.max_range = 0 # the maximum range over the days in the month.
    
    def add_terms(self, new_terms):
        """Add some new terms for this output level.  The overall terms vary
        depending on how many you want from the top per day over the month."""

        self.overall_terms.extend([term for term in new_terms \
                                   if term not in self.overall_terms])

def data_pull(database_file, query):
    """Pull the data from the database."""
    
    user_data = {}
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    
    for row in conn.cursor().execute(query):
        if row['text'] is not None:
            data = tweetclean.cleanup(row['text'], True, True)
            twt = tweetdate.TweetTime(row['created'])
            uid = row['owner']
            
            # could probably get away with pushing this up -- like in c++.
            mdv = twt.get_month()["day_val"]

            try:
                user_data[uid].add_data(mdv, data)
            except KeyError:
                user_data[uid] = frame.FrameUser(uid, mdv, data)

    conn.close()

    return user_data

def text_create(text_name, dictionary, data):
    """Dump the matrix as a csv file."""

    with open(text_name + '.txt', "w") as fout:
        fout.write(vectorspace.dump_raw_matrix(dictionary, data))
        fout.write("\n")

def usage():
    """Standard usage message."""

    print "%s <config_file>" % sys.argv[0]

def main():
    """Main."""

    if len(sys.argv) != 2:
        usage()
        sys.exit(-1)

    # -------------------------------------------------------------------------
    # Parse the parameters.
    config = SafeConfigParser()
    config.read(sys.argv[1])

    database_file = config.get('input', 'database_file')
    year_val = config.getint('input', 'year')
    month_str = config.get('input', 'month')
    stop_file = config.get('input', 'stopwords')
    remove_singletons = config.getboolean('input', 'remove_singletons')
    build_images = config.getboolean('input', 'build_images')
    build_csv_files = config.getboolean('input', 'build_csv_files')

    if month_str not in tweetdate.MONTHS:
        usage()
        sys.exit(-2)

    output_set = {}
    
    for section in config.sections():
        if section.startswith("run"):
            output_folder = config.get(section, 'output_folder')
            
            output_set[section] = \
                Output(
                       output_folder,
                       config.getint(section, 'request_value'))

            try:
                os.stat(output_folder)
            except OSError:
                os.mkdir(output_folder)

    # -------------------------------------------------------------------------
    # Pull stop words
    stopwords = tweetclean.import_stopwords(stop_file)

    kickoff = \
"""
-------------------------------------------------------------------
parameters  :
  database  : %s
  year      : %d
  month     : %s
  output    : %s
  stop      : %s
  count     : %s
  remove    : %s
-------------------------------------------------------------------
"""

    print kickoff % \
        (database_file, 
         year_val,
         month_str,
         str([output_set[output].output_folder for output in output_set]),
         stop_file,
         str([output_set[output].request_value for output in output_set]),
         remove_singletons) 

    # this won't return the 3 columns we care about.
    query_prefetch = \
"""select owner, created, contents as text
from tweets
where created like '%%%s%%%d%%';"""

    # -------------------------------------------------------------------------
    # Build a set of documents, per user, per day.
    num_days = \
        calendar.monthrange(year_val, int(tweetdate.MONTHS[month_str]))[1]
    user_data = \
        data_pull(database_file, query_prefetch % (month_str, year_val))
    full_users = frame.find_full_users(user_data, stopwords, num_days)

    print "data pulled"
    print "user count: %d" % len(user_data)
    print "full users: %d" % len(full_users)

    # -------------------------------------------------------------------------
    # I don't build a master tf-idf set because the tf-idf values should... 
    # evolve.  albeit, I don't think I'm correctly adjusting them -- I'm just 
    # recalculating then.
    #
    # Calculate daily tf-idf; then build frame from top terms over the period
    # of days.
    frames = {}

    for day in range(1, num_days + 1):
        # This is run once per day overall.
        frames[day] = frame.build_full_frame(full_users, user_data, day)
        frames[day].calculate_tfidf(stopwords, remove_singletons)

        # This is run once per day per output.
        for output in output_set:
            out = output_set[output]
            out.add_terms(frames[day].top_terms_overall(out.request_value))
        
            # get_range() is just whatever the last time you ran 
            # top_terms_overall
            new_range = frames[day].get_range()
        
            # This way the images are created with the correct range to cover 
            # all of them.
            if out.max_range < new_range:
                out.max_range = new_range
        
        break
        #if day == 3:
            #break # just do first day.

    print "Frames created"

    # len(overall_terms) should be at most 250 * num_users * num_days -- if 
    # there is no overlap of high value terms over the period of days between 
    # the users.  If there is literally no overlap then each user will have 
    # their own 250 terms each day. 

    # -------------------------------------------------------------------------
    # Dump the matrix.
    for day in frames: # sort if for one file.
        for output in output_set:
            out = output_set[output]
            fname = os.path.join(out.output_folder, "%d" % day)

            #print "out: %s; day: %d: cols: %d" \
                #% (out.output_folder, day, len(frames[day].get_tfidf()))

            if build_csv_files:
                text_create(
                            fname,
                            out.overall_terms,
                            frames[day].get_tfidf())

            if build_images:
                imageoutput.image_create(
                                         fname,
                                         out.overall_terms,       # dictionary
                                         frames[day].get_tfidf(), # data
                                         out.max_range,
                                         'black')

                imageoutput.image_create_color(
                                               fname,
                                               out.overall_terms,  # dictionary
                                               frames[day].get_tfidf(), # data
                                               out.max_range)

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
