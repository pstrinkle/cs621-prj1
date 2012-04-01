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
from ConfigParser import SafeConfigParser

sys.path.append(os.path.join("..", "tweetlib"))
import tweetclean
import tweetdate

sys.path.append(os.path.join("..", "modellib"))
import vectorspace

class Frame():
    """This holds the data for a given day for a set of users."""
    
    def __init__(self, day_val):
        self.day = day_val
        self.data = {}
        self.doc_tfidf = None
        self.doc_freq = None
    
    def add_data(self, user_id, data):
        """Add data to this frame for a user given an id value and their 
        data."""
        
        self.data[user_id] = data

    def calculate_tfidf(self, stopwords, rm_singletons=False):
        """Calculate the tf-idf value for the documents involved."""
        
        # does not remove singletons.
        self.doc_tfidf, self.doc_freq = \
            vectorspace.build_doc_tfIdf(self.data, stopwords, rm_singletons)
    
    def get_tfidf(self):
        """Run calculate_tfidf first or this'll return None."""
        
        return self.doc_tfidf
    
    def top_terms(self, count):
        """Get the top terms from all the columns within a frame.
        
        len(terms) is at most the number of users for a given frame X count.
        """
        
        terms = []

        for doc_id in self.doc_tfidf:
            new_terms = vectorspace.top_terms(self.doc_tfidf[doc_id], count)

            # new_terms is always a set.
            terms.extend([term for term in new_terms if term not in terms])

        return terms

    def top_terms_overall(self, count):
        """Get the top terms overall for the entire set of columns.
        
        len(terms) is actually count.
        """
        
        # Interestingly, many columns can have similar top terms -- with 
        # different positions in the list...  So, this will have to be taken 
        # into account.  Build the overall list and then sort it, then get the
        # first count of the unique...
        #        
        terms = {}
        
        for doc_id in self.doc_tfidf:
            new_tuples = \
                vectorspace.top_terms_tuples(self.doc_tfidf[doc_id], count)

            # These are the top tuples for doc_id; if they are not new, then 
            # increase their value to the new max.            
            for kvp in new_tuples:
                if kvp[0] in terms:
                    terms[kvp[0]] = max(kvp[1], terms[kvp[0]])
                else:
                    terms[kvp[0]] = kvp[1]

        # terms is effectively a document now, so we can use this.
        return vectorspace.top_terms(terms, count)

class FrameUser():
    """Given a user, this holds their daily data."""

    def __init__(self, user_id, day_val, text):
        self.data = {} # tweets collected given some day...?
        self.user_id = user_id
        self.add_data(day_val, text)

    def __len__(self):
        return len(self.data)

    def add_data(self, day_val, text):
        """Add a data to a user's day."""

        try:
            self.data[day_val].append(text)
        except KeyError:
            self.data[day_val] = []
            self.data[day_val].append(text)

    def has_data(self, day_val):
        """Does this user have tweets for that day."""
        
        if day_val in self.data:
            return True
        return False

    def get_data(self, day_val):
        """Get text for this user from that day."""
        
        if day_val in self.data:
            return " ".join(self.data[day_val])
        return None

    def get_alldata(self):
        """Get all the documents as one."""
        
        data = []
        for day in self.data:
            data.extend(self.data[day])
        
        return " ".join(data)

    def get_id(self):
        """What is the id of the user."""
        
        return self.user_id

def find_full_users(users, year, month):
    """Which users have tweets for every day in the month (and year)."""

    num_days = calendar.monthrange(year, int(tweetdate.MONTHS[month]))[1]
    
    # users is a dictionary of FrameUsers key'd on their user id.    
    return [user for user in users if len(users[user]) == num_days]

def build_full_frame(user_list, user_data, day):
    """Build tf-idf for that day."""

    frm = Frame(day)

    for user in user_list:
        frm.add_data(user, user_data[user].get_data(day))

    return frm

def build_dictionary(docs, stopwords):
    """docs is a dictionary of documents."""
    
    words = []
    
    for doc_id in docs:
        pruned = \
            set([w for w in docs[doc_id].split(' ') \
                    if w not in stopwords and len(w) > 1])

        if len(pruned) < 2:
            continue
        
        words.extend([w for w in pruned if w not in words])
    
    return words

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
                user_data[uid] = FrameUser(uid, mdv, data)

    conn.close()

    return user_data

def text_create(text_name, dictionary, data):
    """Dump the matrix as a csv file."""

    with open(text_name + '.txt', "w") as fout:
        fout.write(vectorspace.dump_raw_matrix(dictionary, data))
        fout.write("\n")

def image_create(file_name, dictionary, data):
    """Dump the matrix as a grey-scale bmp file."""

    from PIL import Image
    import math
    
    width = len(data) # Each column is a document within data
    height = len(dictionary) # Each row is a term.
    
    black = 0
    
    # for greyscale.
    img = Image.new('L', (width, height))
    pix = img.load()
    
    # This code is identical to the method used to create the text file.
    # Except because it's building bitmaps, I think it will be flipped. lol.
    sorted_docs = sorted(data.keys())  
    sorted_terms = sorted(dictionary)
  
    # Print Term Rows
    # with L the pixel value is from 0 - 255 (black -> white)
    for i in range(len(sorted_terms)):
        for j in range(len(sorted_docs)):
            # for each row, for each column
            if sorted_terms[i] in data[sorted_docs[j]]:
               val = math.log10(data[sorted_docs[j]][sorted_terms[i]] + 1)
               val %= 2
               pix[j, i] = math.ceil(128 * val)
            else:
                pix[j, i] = black # i is row, j is column.
    
    img.save(file_name + '.png')

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
    year_val = int(config.get('input', 'year'))
    month_str = config.get('input', 'month')
    stop_file = config.get('input', 'stopwords')
    output_folder = config.get('input', 'output_folder')
    request_value = int(config.get('input', 'request_value'))
    remove_singletons = config.getboolean('input', 'remove_singletons')

    if month_str not in tweetdate.MONTHS:
        usage()
        sys.exit(-2)

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
  count     : %d
  remove    : %s
-------------------------------------------------------------------
"""

    print kickoff % \
        (database_file, 
         year_val,
         month_str,
         output_folder,
         stop_file,
         request_value,
         remove_singletons) 

    # this won't return the 3 columns we care about.
    query_prefetch = \
"""select owner, created, contents as text
from tweets
where created like '%%%s%%%d%%';"""

    # -------------------------------------------------------------------------
    # Build a set of documents, per user, per day.
    user_data = \
        data_pull(database_file, query_prefetch % (month_str, year_val))
    full_users = find_full_users(user_data, year_val, month_str)

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
    overall_terms = []

    num_days = \
        calendar.monthrange(year_val, int(tweetdate.MONTHS[month_str]))[1]

    for day in range(1, num_days + 1):
        frames[day] = build_full_frame(full_users, user_data, day)
        frames[day].calculate_tfidf(stopwords, remove_singletons)

        new_terms = frames[day].top_terms_overall(request_value)

        overall_terms.extend([term for term in new_terms \
                                if term not in overall_terms])

    print "total overall: %d" % len(overall_terms)
    print "---- terms ----\n%s\n---- end terms ----" % str(overall_terms)
    # len(overall_terms) should be at most 250 * num_users * num_days -- if 
    # there is no overlap of high value terms over the period of days between 
    # the users.  If there is literally no overlap then each user will have 
    # their own 250 terms each day. 

    # -------------------------------------------------------------------------
    # Dump the matrix.
    for day in frames: # sort if for one file.
        fname = os.path.join(output_folder, "%d" % day)
        text_create(fname, overall_terms, frames[day].get_tfidf())
        image_create(fname, overall_terms, frames[day].get_tfidf())

    # -------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
