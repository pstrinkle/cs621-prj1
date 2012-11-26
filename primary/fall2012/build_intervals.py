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
from json import dumps, loads, JSONEncoder
from operator import itemgetter
from datetime import datetime, timedelta

sys.path.append("modellib")
import vectorspace

class BoringMatrix():
    """This is a boring matrix."""

    def get_json(self):
        dct = {"__BoringMatrix__" : True}
        dct["matrix"] = self.term_matrix
        dct["weights"] = self.term_weights
        dct["count"] = self.total_count
        
        return dct

    def __init__(self, matrix, weights, count):
        """Create from whatever."""
        self.term_matrix = matrix
        self.term_weights = weights
        self.total_count = count

    def __init__(self, bag_of_words):
        """Initialize this structure with a long string."""
        
        self.term_matrix = {}
        self.term_weights = {}
        self.total_count = 0
        self.add_bag(bag_of_words)

    def compute(self):
        """Run the basic term weight calculation."""
        
        # None of these are zero.
        for term in self.term_matrix:
            self.term_weights[term] = (float(self.term_matrix[term]) / self.total_count)
    
    def add_bag(self, bag_of_words):
        """Add a bag of words to the current matrix."""
        
        if bag_of_words is None:
            return
        
        for word in bag_of_words.split(" "):
            try:
                self.term_matrix[word] += 1
            except KeyError:
                self.term_matrix[word] = 1
            self.total_count += 1

def as_boring(dct):
    """Build a boring object from a dictionary from a boring matrix."""
    if '__BoringMatrix__' in dct:
        return BoringMatrix(dct["matrix"], dct["weights"], dct["count"])
    return dct

class BoringMatrixEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BoringMatrix):
            return obj.get_json()
        return JSONEncoder.default(self, obj)

# consider moving this to a library since it lives here and in identify_stopwords.
def localclean(text):
    """Locally clean the stuff, replace #'s and numbers."""
    
    neat = text.replace("#", " ")
    neat = neat.replace("$", " ")
    neat = neat.replace("`", " ")
    neat = neat.replace("%", " ")
    
    neat = neat.replace("0", " ")
    neat = neat.replace("1", " ")
    neat = neat.replace("2", " ")
    neat = neat.replace("3", " ")
    neat = neat.replace("4", " ")
    neat = neat.replace("5", " ")
    neat = neat.replace("6", " ")
    neat = neat.replace("7", " ")
    neat = neat.replace("8", " ")
    neat = neat.replace("9", " ")
    
    neat = neat.replace("-", "")
    
    return neat

def datetime_from_long(timestamp):
    """Convert a timestamp to a datetime.datetime."""

    timeasstr = str(timestamp)

    year = int(timeasstr[0:4])
    month = int(timeasstr[4:6])
    day = int(timeasstr[6:8])
    hour = int(timeasstr[8:10])
    minute = int(timeasstr[10:12])
    second = int(timeasstr[12:14])

    return datetime(year, month, day, hour, minute, second)

def long_from_datetime(dt):
    """Convert a datetime object to an integer."""
    
    return int(dt.strftime("%Y%m%d%H%M%S"))

def usage():
    """."""

    print "usage: %s <sqlite_db> <stopwords.in> <singletons.in> <output_file> <interval in seconds> <note begins>" % sys.argv[0]
    
    # XXX: I would use pickle, but these are human-readable.
    print "\tsqlite_db := the input database."
    print "\tstopwords.in := json dump of a stop word array."
    print "\tsingletons.in := json dump of a single word array."
    print "\toutput_file := currently just dumps whatever the current meaning of results is."
    print "\tinterval in seconds := is the time slicing to use."
    print "\tnote begins := the note column in the sqlite_db starts with this text."

def main():
    """."""

    # Did they provide the correct args?
    if len(sys.argv) != 7:
        usage()
        sys.exit(-1)

    # --------------------------------------------------------------------------
    # Parse the parameters.
    database_file = sys.argv[1]
    stopwords_file = sys.argv[2]
    singletons_file = sys.argv[3]
    
    output_name = sys.argv[4]
    interval = int(sys.argv[5])
    note_begins = sys.argv[6]

    with open(stopwords_file, 'r') as fin:
        stopwords = loads(fin.read())
    
    with open(singletons_file, 'r') as fin:
        singletons = loads(fin.read())
    
    remove_em = []
    remove_em.extend(stopwords)
    remove_em.extend(singletons)

    # this won't return the 3 columns we care about.
    # XXX: This doesn't select by note.
    query = "select id, cleaned_text from tweets where note like '%s%%' and (yyyymmddhhmmss >= %d and yyyymmddhhmmss < %d);"

    # --------------------------------------------------------------------------
    # Search the database file for the earliest timestamp and latest.

    early_query = "select min(yyyymmddhhmmss) as early, max(yyyymmddhhmmss) as late from tweets;"
    earliest = 0
    latest = 0

    with sqlite3.connect(database_file) as conn: 
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute(early_query)
        row = curr.fetchone()

        earliest = row['early']
        latest = row['late']

    # the timestamps are YYYYMMDDHHMMSS -- so I need to convert them into 
    # datetime.datetime objects; easy.
    # okay, so they want the timestamps to step forward slowly.
    # can use datetime.timedelta correctly updates the datetime value, which
    # we'll then need to convert back to the timestamp long.

    starttime = datetime_from_long(earliest)
    endtime = datetime_from_long(latest)
    currtime = starttime
    delta = timedelta(0, interval)

    # datetime.timedelta(0, 1) (days, seconds)
    # you can just add these to datetime.datetime objects.
    #
    # (endtime - starttime) gives you a datetime.timedelta object.

    print "starttime: %s" % starttime
    print "endtime: %s" % endtime
    
    results = {}

    # --------------------------------------------------------------------------
    # Search the database file for certain things.
    with sqlite3.connect(database_file) as conn:
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        
        while currtime + delta < endtime:
            start = long_from_datetime(currtime)
            currtime += delta
            end = long_from_datetime(currtime)
            
            results[start] = []
            
            print "range: %d %d" % (start, end)
            
            # build the text for that time-slice into one document, removing
            # the stopwords provided by the user as well as the singleton
            # list, neatly also provided by the user.

            for row in curr.execute(query % (note_begins, start, end)):
                results[start].append(localclean(row['cleaned_text']))
            
            tmp_local = " ".join(results[start]) # join into one line
            # then split and strip out bad words.
            results[start] = BoringMatrix(" ".join([word for word in tmp_local.split(" ") if word not in remove_em and len(word) > 2]))
            results[start].compute()
            
            #print dumps(results, cls=BoringMatrixEncoder, indent=4)
            #sys.exit(0)

    with open(output_name, 'w') as fout:
        fout.write(dumps(results, cls=BoringMatrixEncoder, indent=4))
    
    # results = json.loads(results.in, object_hook=as_boring)

    # --------------------------------------------------------------------------
    # Done.

if __name__ == "__main__":
    main()
