#!/usr/bin/env python
"""
Provide summary statistics for a JSONL file, where each line contains a JSON-formatted tweet 
as retrieved from the Twitter API.

Sample usage:
python jsonl-tweet-stats.py sample/sample-tweets-500.jsonl
"""
import sys, fileinput, operator
from optparse import OptionParser
from collections import defaultdict
import logging as log
try:
	import ujson as json 
except:
	import json

# --------------------------------------------------------------

class TweetCounter:
	def __init__( self ):
		self.num_retweets = 0
		self.num_replies = 0
		self.has_hashtags = 0
		self.has_urls = 0
		self.has_mentions = 0
		self.num_geo = 0
		self.lang_counts = defaultdict(int)

	def apply( self, tweet ):
		retweeted = tweet.get("retweeted_status",None) is not None
		if retweeted:
			self.num_retweets += 1
		if not tweet["in_reply_to_user_id"] is None:
			self.num_replies += 1
		if not tweet["geo"] is None:
			self.num_geo += 1
		ents = tweet.get("entities",[])
		if len(ents["hashtags"]) > 0:
			self.has_hashtags += 1
		if len(ents["urls"]) > 0:
			self.has_urls += 1
		if len(ents["user_mentions"]) > 0:
			self.has_mentions += 1
		# counts of specific items
		if "lang" in tweet:
			self.lang_counts[tweet["lang"]] += 1

# --------------------------------------------------------------

def per( x, total ):
	if total == 0:
		return "0%"
	return "%.2f%%" % ( (100.0*x)/total )

def counts_to_str( counts, top = -1 ):
	sx = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
	if top > 0:
		sx = sx[0:min(top,len(sx))]
	slist = [ "%s (%d)" % ( p[0], p[1] ) for p in sx ]
	return ", ".join( slist )

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] json_file1 json_file2 ...")
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')

	for tweets_path in args:
		log.info("Loading tweets from %s ..." % tweets_path)

		# Process every line as JSON data
		num_tweets, num_failed, line_number = 0, 0, 0
		counter = TweetCounter()
		for l in fileinput.input(tweets_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				tweet = json.loads(l)
				counter.apply( tweet )
				num_tweets += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()

		# Display basic stats for this file
		log.info("Total: %d tweets, %d failed" % (num_tweets,num_failed))
		log.info("Retweets: %d (%s)" % (counter.num_retweets, per(counter.num_retweets,num_tweets) ) )
		log.info("Replies: %d (%s)" % (counter.num_replies, per(counter.num_replies,num_tweets) ) )
		log.info("Geotagged Tweets: %d (%s)" % (counter.num_geo, per(counter.num_geo,num_tweets) ) )
		log.info("Tweets with URL: %d (%s)" % (counter.has_urls, per(counter.has_urls,num_tweets) ) )
		log.info("Tweets with Mentions: %d (%s)" % (counter.has_mentions, per(counter.has_mentions,num_tweets) ) )
		log.info("Top Languages: %s" % counts_to_str( counter.lang_counts, 10 ) )

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
