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

sys.path.append("tweetlib")
import TweetXml

def getRateStatus(api):
  """
  Given an api object, call GetRateLimitStatus() and if it throws a "Capacity Error" 
  continue calling until it doesn't, with a 2 second pause.  Any other exceptions are
  passed up.
  
  Input: api := Twitter.api object
  
  Return: RateLimit dictionary.  See python-twitter docs.
  """

  success = 0
  rate_status = None
  
  # while the API call fails for capacity error reasons:
  while success == 0:
    try:
      rate_status = api.GetRateLimitStatus()
      success = 1
    except twitter.TwitterError, e:
      if e.message == "Capacity Error":
        print "capacity error on getRateStatus"
        pass
      else:
        break
  
  if rate_status == None:
    sys.stderr.write("could not get api rate limit status!\n")
    sys.exit(-1)
  
  return rate_status

def usage():
  usageStr =\
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

  consumer_key = 'IoOS13WALONePQbVoq9ePQ'
  consumer_secret = 'zjf2HsUqe6FHdwy81lX93BOuk8NFT9jGdBZTprAhY'
  access_token_key = '187244615-s3gCVJNg9TZJPlIEW7yFKHYPXi2xf3lpQnv9uDNV'
  access_token_secret = 'Hig5HYmDqv7j7cM4LxZExpXKcKfWs1Xb5sWRU24Bg5E'
  
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
  # API key == IoOS13WALONePQbVoq9ePQ
  # Consumer key == IoOS13WALONePQbVoq9ePQ
  # Consumer secret == zjf2HsUqe6FHdwy81lX93BOuk8NFT9jGdBZTprAhY
  # Your Twitter Access Token key: 187244615-s3gCVJNg9TZJPlIEW7yFKHYPXi2xf3lpQnv9uDNV
  # Access Token secret: Hig5HYmDqv7j7cM4LxZExpXKcKfWs1Xb5sWRU24Bg5E
  #
  api = twitter.Api(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token_key=access_token_key,
                    access_token_secret=access_token_secret)


  # ---------------------------------------------------------------------------
  # Collect Tweets.

  tweets_collected = []
  rate_status = getRateStatus(api)
  
  publicCnt = 0
  
  while publicCnt < publicRequest:
    rate_status = getRateStatus(api)
    print "publicCnt: %d" % publicCnt
    remains = rate_status['remaining_hits']
    print "remains: %d" % remains
    
    if remains < 2:
      # this is seconds since the epoch.
      reset_time = int(rate_status['reset_time_in_seconds'])
      my_time = calendar.timegm(time.gmtime())
      min_wait = (reset_time - my_time) / 60
      sec_wait = (reset_time - my_time) - (min_wait *60)
      
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

