#!/usr/bin/env python
"""
Provide list of the most frequently-appearing hashtags for a JSONL file, where each line contains a JSON-formatted tweet 
as retrieved from the Twitter API.

Sample usage:
python jsonl-tweet-hashtags.py sample/sample-tweets-500.jsonl
"""
import sys, fileinput, operator
from optparse import OptionParser
from collections import defaultdict
import logging as log
try:
	import ujson as json 
except:
	import json
from prettytable import PrettyTable

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] json_file1 json_file2 ...")
	parser.add_option("-t", "--top", action="store", type="int", dest="top", help="number of top hashtags to display", default=10)
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')

	for tweets_path in args:
		log.info("Loading tweets from %s ..." % tweets_path)
		
		# Process every line as JSON data
		hashtags = {}
		num_tweets, num_failed, line_number, has_hashtags = 0, 0, 0, 0
		counts = defaultdict(int)
		for l in fileinput.input(tweets_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				tweet = json.loads(l)
				if "entities" in tweet:
					if "hashtags" in tweet["entities"] and len(tweet["entities"]["hashtags"]) > 0:
						has_hashtags += 1
						for tag in tweet["entities"]["hashtags"]:
							text = "#" + tag["text"].lower().strip()
							counts[text] += 1
				num_tweets += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()
		log.info("Found %d/%d tweets containing at least one hashtag. File has %d distinct hashtags" % ( has_hashtags, num_tweets, len(counts) ) )

		# Display the top hashtags for this file
		sx = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
		log.info("Top %d hashtags appearing in tweets:" % min( len(sx), options.top ) )
		tab = PrettyTable( ["Hashtag", "Count"] )
		tab.align["Hashtag"] = "l"
		tab.align["Count"] = "r"
		for i, pair in enumerate(sx):
			if i > options.top:
				break
			tab.add_row( pair )
		log.info(tab)

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
