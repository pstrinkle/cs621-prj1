#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# This attempts to collate the tweet files and remove duplicates
# given an entire folder of xml files, instead of using sort/uniq
# on a per file basis.
#
# Run tweets_by_user.py

import sys
import sqlite3

sys.path.append("modellib")
import vectorspace

def usage():
    print "usage: %s <sqlite_db> <output_file>" % sys.argv[0]

def main():
    global output_name

    # Did they provide the correct args?
    if len(sys.argv) != 3:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    output_name = sys.argv[2]
    
    print "database folder: %s\noutput file: %s" \
        % (database_file, output_name)

    # this won't return the 3 columns we care about.
    query = "select id, contents as text from tweets;"

    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row

    c = conn.cursor()

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    
    docs = {}
    stopwords = []
    
    for row in c.execute(query):
        print row['id']
        docs[row['id']] = row['text']

    tfidf, dictionary = vectorspace.build_doc_tfidf(docs, stopwords, True)
    
    vectorspace.dump_matrix(dictionary, tfidf)

    # --------------------------------------------------------------------------
    # Done.
    conn.close()

if __name__ == "__main__":
    main()
