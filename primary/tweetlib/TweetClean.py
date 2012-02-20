#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Summer 2011
#
# This handles cleaning tweets.  These things have a very specific format.
#

import re

def importStopWords(location):
  """
  Given a file location, read in the stop words.
  """
  with open(location, "r") as f:
    stopwords = f.readlines()

    # clean them up!
    for i in xrange(0, len(stopwords)):
      stopwords[i] = stopwords[i].strip()
  
  return stopwords

def extract_id(tweet):
  """
  Given a line from my XML file of tweets, return a tuple (tweet_id, tweet_contents)
  """
  idRe = re.search('<id>(.*?)</id>', tweet)
  textRe = re.search('<text>(.*?)</text>', tweet)
  
  if idRe == None or textRe == None:
    print "you have a formatting error"
    return None
  
  return (idRe.group(1), textRe.group(1))

def extract(tweet):
  """
  Given a line from my XML file of tweets, return a tuple (date string, tweet contents)
  
  The date string is a string in this, and the tweet is not cleaned.
  """
  createdRe = re.search('<created>"(.*?)"</created>', tweet)
  textRe = re.search('<text>"(.*?)"</text>', tweet)
  
  if createdRe == None or textRe == None:
    print "you have a formatting error"
    return None
  
  return (createdRe.group(1), textRe.group(1))

def cleanup(tweet, lowercase = True, to_ascii = False):
  """
  Clean up the string in all the pretty ways.
  
  Input: tweet := the text body of the tweet, so far I've been trying to process these as utf-8
                  and let python handle the stuff... but that may not work if I leave the English
                  base.
         lowercase := defaults to True, would you like the tweet moved entirely into lowercase?
         
         to_ascii := defaults to False, would you like only the valid ascii characters used?
         
         Only set to_ascii as true if you read the file in with codecs.open()!
  
  Output: Cleaned tweet string.
  
  This currently removes any @username mentions, extraneous newlines, parentheses, and most if not all
  punctuation.  It does leave in apostrophies.
  """
  
  if to_ascii:
    tweet = tweet.encode('ascii', errors='ignore')
  
  newTweet = tweet.replace("\n", ' ')     # newline character
  newTweet = newTweet.replace(r"\n", ' ') # newline string (yes, there are those)
  newTweet = newTweet.replace(',', ' ')   # commas provide nothing to us
  newTweet = newTweet.replace(r"\t", ' ') # tab string (yes, there are those)

  # make it lowercase -- important so that the I don't get caught up in case;
  # although in the future i may want that distinction.
  # TODO: Remove this call if we want case sensitivity.
  if lowercase:
    newTweet = newTweet.lower()

  # I really should try to remove any URLs in here, and chances are there is only 1.
  # Really need to add in re.IGNORECASE if you remove the lower() call above.
  url = re.search(r'(http://\S+)', newTweet)

  if url != None:
    newTweet = newTweet.replace(url.group(1), '')
    
  # Could for the most part just use ascii char available.
  newTweet = newTweet.replace("&gt;", ">") # html to character
  newTweet = newTweet.replace("&lt;", "<") # html to character
  newTweet = newTweet.replace("&amp;", "&") # html to character

  # excessive backslashing
  # periods.  Safe to remove only after you've cleared out the URLs
  # excessive forward-slashing
  # emphasis dashes
  # topic tag TODO: Removing this unweighs the term. <-- leaving in place for now.
  replacements = [
                  '.', '/', '(', ')', '!', '?', '"', ':', ";", "&", "*", '^', 
                  '>', '<', '+', '=', '_', ',', '[', ']', '{', '}', '|', 
                  '\\', "--"]

  for r in replacements:
    newTweet = newTweet.replace(r, ' ')
  
  # There could be a few usernames in the tweet...
  user = re.search('(@\S+)', newTweet)

  while user != None:
    newTweet = newTweet.replace(user.group(1), '')
    user = re.search('(@\S+)', newTweet)
  
  newTweet = newTweet.replace("@", '')   # at sign
  #newTweet = newTweet.replace('-', ' ')  # hyphen (us-1, i-95)
  # XXX: I would like to however, remove -x or x-... can use regex... 
  newTweet = newTweet.replace("'", '') # makes don't -> dont
  
  extraSpace = re.search('(\s{2})', newTweet)
  
  while extraSpace != None:
    newTweet = newTweet.replace(extraSpace.group(1), ' ')
    extraSpace = re.search('(\s{2})', newTweet)

  newTweet = newTweet.strip()

  return newTweet
