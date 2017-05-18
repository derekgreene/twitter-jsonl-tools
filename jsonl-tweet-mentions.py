#!/usr/bin/env python
"""
Provide list of the most frequently-mentioned users for a JSONL file, where each line contains a JSON-formatted tweet 
as retrieved from the Twitter API.

Sample usage:
python jsonl-tweet-mentions.py sample/sample-tweets-500.jsonl
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
	parser.add_option("-t", "--top", action="store", type="int", dest="top", help="number of top users to display", default=10)
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')

	for tweets_path in args:
		log.info("Loading tweets from %s ..." % tweets_path)
		
		# Process every line as JSON data
		users = {}
		num_tweets, num_failed, line_number, has_mentions = 0, 0, 0, 0
		counts = defaultdict(int)
		for l in fileinput.input(tweets_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				tweet = json.loads(l)
				if "entities" in tweet:
					if "user_mentions" in tweet["entities"] and len(tweet["entities"]["user_mentions"]) > 0:
						has_mentions += 1
						for user in tweet["entities"]["user_mentions"]:
							user_id = user["id"]
							if not user_id in users:
								users[user_id] = user
							counts[user_id] += 1
				num_tweets += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()
		log.info("Found %d/%d tweets containing at least one user mention. %d distinct users were mentioned." % ( has_mentions, num_tweets, len(users) ) )

		# Display the top mentions for this file
		sx = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
		log.info("Top %d users by mentions:" % min( len(sx), options.top ) )
		tab = PrettyTable( ["Screen Name", "User ID", "Full Name", "Count"] )
		tab.align["Screen Name"] = "l"
		tab.align["User ID"] = "l"
		tab.align["Full Name"] = "l"
		tab.align["Count"] = "r"
		for i, pair in enumerate(sx):
			if i > options.top:
				break
			user = users[pair[0]]
			tab.add_row( [ user["screen_name"], str(pair[0]), user["name"], pair[1] ] )
		log.info(tab)


# --------------------------------------------------------------

if __name__ == "__main__":
	main()
