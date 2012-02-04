#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2011/Summer 2011
#
# The goal of this simple script is to run various queries against Twitter through
# the published API, using the python-twitter open source library.
#

import os
import sys
import re
import datetime
import time
import calendar
import twitter
import codecs
import urllib2 # for the exception
import httplib # for the exception

sys.path.append("tweetlib")
import TweetXml
import TweetRequest

def usage():
  usageStr =\
  """
  usage: %s (-ts|-both) <users_input_filename> <output_folder> <error_log> <kill_file> <success_log>
  
      -ts := pull tweets
      users_input_filename := this is a file of the following format: "<id>id</id>..."
      output_folder := where you want the paired files created:
          the statuses are placed in files, id_date.xml
          the friends are placed in files, id_friends.txt
      error_log := this will hold the exceptions that we catch during processing.
      kill_file := if this file suddenly exists the program will cleaning stop executing.
  """
  print usageStr % sys.argv[0]

def main():

  if len(sys.argv) != 7:
    usage()
    sys.exit(-1)
  
  startTime = datetime.datetime.now()
  
  # Looks like I need to update the library or figure out how to get to the oauth stuff from it;
  # I built my own application thing and have my own oauth stuff.
  #
  api = twitter.Api()

  users = []
  
  paramaters = sys.argv[1]
  file_input = sys.argv[2]
  folder_output = sys.argv[3]
  file_errors = sys.argv[4]
  file_kill = sys.argv[5]
  file_fin = sys.argv[6]
  
  pull_statuses = 0
  pull_friends = 0
  
  if paramaters == "-ts":
    pull_statuses = 1
  else:
    usage()
    sys.exit(-1)

  # ---------------------------------------------------------------------------
  # Read in user list file.
  with open(file_input, "r") as f:
    users_raw = f.readlines()
    for i in users_raw:
      urs = re.search(r"<id>(\d+?)</id><last_since_id>(\d+?)</last_since_id><oldest_id>(\d+?)</oldest_id>", i)
      onlyid = re.search("<id>(\d+?)</id>", i)
      if urs and urs.group(1) not in users:
        # In this case we want to make since_id to be 0 so we can go back in time
        # and we set max_id to be the last time we pulled.. in the future this will be the
        # oldest tweet_id.
        #
        # Once we've run backlog on our users we don't really need to go too far into the past;
        # Albeit it'd be a good idea to properly handle going back in time to an extent if we
        # miss some.
        #
        # Ugh.  I need to get some work done on this.
        users.append(TweetRequest.RequestTuple(int(urs.group(1)), 0, int(urs.group(3))))
      elif onlyid and onlyid.group(1) not in users:
        users.append(TweetRequest.RequestTuple(int(onlyid.group(1))))
  
  print "users to pull: %d" % len(users)
  
  # open error log:
  err = open(file_errors, "w")
  
  # open success log:
  fin = open(file_fin, "w")

  # ---------------------------------------------------------------------------
  # For each user in the users input file.
  users.sort(key=lambda request: request.user_id)
  
  # For each user:
  for user in users:
    
    print "processing: %d" % user.user_id
    
    # FYI, this API can only get me 3500 tweets back--that being said, I want to hit each user
    # repeatedly until no more come out, even if the last one is a wasted call.
    done = False
    
    while done == False:
      # short-cut out!
      if os.path.exists(file_kill):
        print "prematurely killing"
        break
    
      # Do we need to wait?
      rate_status = TweetRequest.getRateStatus(api)
      remains = rate_status['remaining_hits']
    
      if remains < 1:
        # this is seconds since the epoch.
        reset_time = int(rate_status['reset_time_in_seconds'])
        my_time = calendar.timegm(time.gmtime())
      
        min_wait = (reset_time - my_time) / 60
        sec_wait = (reset_time - my_time) - (min_wait *60)
        print "forced sleep: %dm:%ds" % (min_wait, sec_wait)
        time.sleep((reset_time - my_time))
      else:
        time.sleep(6) # 3600 / 350 ~ 10, so 6.
    
      # If this runs overnight, then the pulls will be from the date I kicked off the script.
      ext = "_%s.xml" % datetime.date.today().isoformat().replace("-","")

      # Given a since_id we know where to start pulling the future.
      # Given a max_id we know where to start pulling the past. 
      try:
        print "\tprocessing: %d, since: %d, max: %d" % (user.user_id, user.since_id, user.max_id)
      
        # Get the timeline (and an updated user information view, sans friends)
        statuses = \
          api.GetUserTimeline(
                              user_id=user.user_id, 
                              since_id=user.since_id,
                              max_id=user.max_id,
                              count=200,
                              include_entities='true')

        if len(statuses) > 0:
          with codecs.open(os.path.join(folder_output, str(user) + ext), "a", 'utf-8') as f:
            for s in statuses:
              f.write(TweetXml.xmlStatus(s))
              # originally the newline was added, but I think this was inadvertently converting it to a string..?
              f.write("\n")
          user.max_id = statuses[len(statuses)-1].id
          user.count += len(statuses)
          print "\ttotal: %d retrieved: %d, new max_id: %d" \
            % (statuses[0].user.statuses_count, len(statuses), user.max_id)
        
        # what if this is a valid new tweet?... I'm fairly certain this tends to be the
        # tweet with max_id == id or something.
        # originally this was only checking for == 1, but the it ran all night and did nothing
        # with user 13, and I'm assuming this was because it returned 0.
        if len(statuses) == 1 or len(statuses) == 0:
          print "len(statuses) == %d, done with user" % len(statuses)
          fin.write("<id>%s</id>\n" % str(user))
          fin.flush()
          done = True

      except twitter.TwitterError, e:
        if e.message == "Capacity Error":
          print "capacity error caught on api.GetUserTimeline(%s) added back in.\n" % str(user)
          users.append(user)
          done = True
          pass
        else:
          err.write("%s on <id>%d</id>\n" % (e.message, user.user_id))
          err.flush()
          done = True
      except urllib2.URLError, e:
        print "%s" % e.message
      except httplib.BadStatusLine, e:
        print "%s" % e.message

  fin.close()
  err.close()

  # ---------------------------------------------------------------------------
  # Done.

  print "total runtime: ",
  print (datetime.datetime.now() - startTime)

if __name__ == "__main__":
  main()
