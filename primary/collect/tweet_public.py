#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# The goal of this simple script is to run various queries against Twitter through
# the published API, using the python-twitter open source library.
#
# TODO: Note, this doesn't really seem to do anything useful yet as each call seems
# to retrieve the same 20 tweets... whereas I would imagine each call would have many
# things.

import os
import sys
import re
import datetime
import time
import calendar
#import glob
import twitter

sys.path.append(os.path.join("..", "tweetlib"))
import tweetxml
import tweetrequest

def usage():
    usageStr = \
    """
    usage: %s <public requests> <output_tweets.xml> <output_users.xml>
    
            users_input_filename := this is a file of the following format: "id name:..."
            output_folder := where you want the paired files created:
                    the statuses are placed in files, id_date.xml
                    the friends are placed in files, id_friends.txt
            error_log := this will hold the exceptions that we catch during processing.
    """
    print usageStr % sys.argv[0]

def main():

    if len(sys.argv) != 4:
        usage()
        sys.exit(-1)
    
    publicRequest = int(sys.argv[1])
    output_tweets = sys.argv[2]
    output_users = sys.argv[3]
    
    startTime = datetime.datetime.now()
    
    # Looks like I need to update the library or figure out how to get to the oauth stuff from it;
    # I built my own application thing and have my own oauth stuff.
    #
    api = twitter.Api(
                      consumer_key=tweetrequest.consumer_key,
                      consumer_secret=tweetrequest.consumer_secret,
                      access_token_key=tweetrequest.access_token_key,
                      access_token_secret=tweetrequest.access_token_secret)


    # ---------------------------------------------------------------------------
    # Collect Tweets.

    tweets_collected = []
    rate_status = tweetrequest.getRateStatus(api)
    
    publicCnt = 0
    
    while publicCnt < publicRequest:
        rate_status = tweetrequest.getRateStatus(api)
        print "publicCnt: %d" % publicCnt
        remains = rate_status['remaining_hits']
        print "remains: %d" % remains
        
        if remains < 2:
            # this is seconds since the epoch.
            reset_time = int(rate_status['reset_time_in_seconds'])
            my_time = calendar.timegm(time.gmtime())
            min_wait = (reset_time - my_time) / 60
            sec_wait = (reset_time - my_time) - (min_wait * 60)
            
            print "forced sleep: %dm:%ds" % (min_wait, sec_wait)
            time.sleep((reset_time - my_time) + 60)
        else:
            time.sleep(3)

        # Okay, try to get the UserTimeline and the Friends for user in users.
        try:
            statuses = api.GetPublicTimeline(include_entities='true')
            
            print "retrieved: %d" % len(statuses)

            for s in statuses:
                if s not in tweets_collected:
                    print "new tweet"
                    tweets_collected.append(s)

        except twitter.TwitterError, e:
            if e.message == "Capacity Error":
                pass
        publicCnt += 1

    # ---------------------------------------------------------------------------
    # Process Tweets.

    for t in tweets_collected:
        print "%s" % t.text.encode('utf-8')


    # ---------------------------------------------------------------------------
    # Done.
    
    print "total runtime: ",
    print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
    main()

