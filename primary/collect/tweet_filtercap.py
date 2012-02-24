#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Fall 2011
#
# 
#

import os
import sys
import codecs
import socket
import tweetstream

sys.path.append(os.path.join("..", "tweetlib"))
import TweetXml as tx

def usage():
  print "usage: %s <count> <output file> <kill_file>" % sys.argv[0]

def main():
  
  socket._fileobject.default_bufsize = 0

  # Did they provide the correct args?
  if len(sys.argv) != 4:
    usage()
    sys.exit(-1)

  max = int(sys.argv[1])
  output = sys.argv[2]
  file_kill = sys.argv[3]

  # ---------------------------------------------------------------------------
  # Grab sample stream of tweets, likely only 1% of all tweets.

  # I-495: ["-77.296,38.71", "-76.643,39.133"]
  # Boston: ["-71.366,42.158", "-70.714,42.551"]
  # Alaska: ["-173.5,57.4", "-131.8,71.7"]
  # Middle East: ["38.4,20.4", "80.1,48"]
  # North America: ["-133.5,17.8", "-50,64.9"]
  # North America 2: ["-133.5,24.7", "-50,64.9"] (less Mexico, etc)
  # Some of Western Europe: ["-4.43,40.91", "16.44,52.51"]
  # Bay Area: ["-122.75,36.8", "-121.75,37.8"]
  # Europe: ["-19.1,19.1", "109.6,64.9"]
  # S. America, S. Africa ["-83.4,-43.8", "45.3,17.5"]
  # US and Canada ["-198.4,-2.4", "-22.1,77.5"]
  # Most of the World ["-184,-63", "169,85"]
  # Should be entire world ["-180,-90", "180,90"]
  # Eastern Europe ["22.7,21.8", "151.4,65.3"]

  count = 0

  #"left,bottom", "right,top"
  locations = ["22.7,21.8", "151.4,65.3"]

  try:
    with codecs.open(output, "w", 'utf-8') as f:
      #with tweetstream.FilterStream("profoundalias", "tschusisgerman1", locations=locations) as stream:
      with tweetstream.FilterStream("umanyannya", "happyluckyboomfuck9", locations=locations) as stream:
        for tweet in stream:
          if os.path.exists(file_kill):
            print "prematurely killing"
            break
          if "user" in tweet:
            print "Got tweet from %-16s\t(tweet %d, rate %.1f tweets/sec)" % (tweet["user"]["screen_name"], stream.count, stream.rate)          
            if "retweeted_status" in tweet:
              pass
            else:
              f.write(tx.statusStrFromDict(tweet) + u"\n")
              f.flush()
              count += 1

            if count > max:
              break

  except tweetstream.ConnectionError, e:
    print "Disconnected from twitter. Reason:", e.reason

  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()
