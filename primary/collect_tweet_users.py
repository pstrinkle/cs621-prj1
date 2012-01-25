#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011
#
# The goal of this simple script is to run various queries against Twitter through
# the published API, using the python-twitter open source library.
#
# TwitterError

import os
import sys
import re
import twitter
import urllib2 # for the exception
import httplib # for the exception

sys.path.append("tweetlib")
import TweetXml

def usage():
  print "usage: %s <input file name> <known friends> <output filename>" % sys.argv[0]
  print "       this is a file of the following format: id #note"
  print "       the output is a utf-8 file of the same format"
  print "       this software can only run 350 queries at a time, so it"
  print "       first walks the input file and collects their friends before it dives into the list."


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
    except urllib2.URLError, e:
      print "exception: %s" % e.message
    except httplib.BadStatusLine, e:
      print "exception: %s" % e.message
  
  if rate_status == None:
    sys.stderr.write("could not get api rate limit status!\n")
    sys.exit(-1)
  
  return rate_status

def main():

  consumer_key = 'IoOS13WALONePQbVoq9ePQ'
  consumer_secret = 'zjf2HsUqe6FHdwy81lX93BOuk8NFT9jGdBZTprAhY'
  access_token_key = '187244615-s3gCVJNg9TZJPlIEW7yFKHYPXi2xf3lpQnv9uDNV'
  access_token_secret = 'Hig5HYmDqv7j7cM4LxZExpXKcKfWs1Xb5sWRU24Bg5E'

  if len(sys.argv) != 4:
    usage()
    sys.exit(-1)

  api = twitter.Api(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token_key=access_token_key,
                    access_token_secret=access_token_secret)

  input_users = []
  new_users = []
  known_users = []

  with open(sys.argv[1], "r") as f:
    users_raw = f.readlines()

  with open(sys.argv[2], "r") as f:
    known_raw = f.readlines()
    for i in known_raw:
      urs = re.search(r"(\d+?) ", i)
      if urs and urs.group(1) not in known_users:
        known_users.append(int(urs.group(1)))

  for i in users_raw:
    urs = re.search(r"(\d+?) ", i)
    if urs and urs.group(1) not in input_users and urs.group(1) not in known_users:
      input_users.append(int(urs.group(1)))
  
  with open(sys.argv[3], "w") as f:
    for user in input_users:
      
      print user # this is basically a progress counter so I know where to kick it off next time.
      
      # Do we need to wait?
      rate_status = getRateStatus(api)
      remains = rate_status['remaining_hits']
    
      if remains < 1:
        # this is seconds since the epoch.
        reset_time = int(rate_status['reset_time_in_seconds'])
        my_time = calendar.timegm(time.gmtime())
      
        min_wait = (reset_time - my_time) / 60
        sec_wait = (reset_time - my_time) - (min_wait *60)
        print "forced sleep: %dm:%ds" % (min_wait, sec_wait)
        sys.stdout.flush()
        time.sleep((reset_time - my_time))
      else:
        time.sleep(6) # 3600 / 350 ~ 10, so 6.
      
      their_users = api.GetFriends(user=user)
      
      for u in their_users:
          # Only pull in friends who share their tweets.
          if u not in input_users and u not in new_users:              
            if u.lang.encode('utf-8') == "en":
              new_users.append(u.id)
              f.write(TweetXml.getUser(u) + "\n")
              # non english language user.  
      remaining = api.GetRateLimitStatus()['remaining_hits']
      if remaining == 0:
        break

  # This will tell me how many more times I can hit their server in the time period.
  # GetRateLimitStatus() returns a dictionary:
  print "How many more hits I can take: %d" % api.GetRateLimitStatus()['remaining_hits']

if __name__ == "__main__":
  main()
