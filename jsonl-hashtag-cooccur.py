#!/usr/bin/env python
"""
Generate a list of hashtag cooccurrence frequencies for one or more JSONL files, where each line contains a JSON-formatted tweet 
as retrieved from the Twitter API.

Sample usage:
python jsonl-hashtag-cooccur.py sample/sample-tweets-500.jsonl -o hashtag-cooccurrences.csv
"""
import sys, fileinput, itertools, operator, codecs
from collections import defaultdict
from optparse import OptionParser
import logging as log
try:
	import ujson as json 
except:
	import json
from prettytable import PrettyTable

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] json_file1 json_file2 ...")
	parser.add_option("-t", "--top", action="store", type="int", dest="top", help="number of top pairs to display", default=10)
	parser.add_option("-o", action="store", type="string", dest="out_path", help="output path", default="hashtag-cooccurrences.csv")
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')

	# Count pairs of hashtags in the same tweet
	pair_counts = defaultdict(int)
	for tweets_path in args:
		log.info("Loading tweets from %s ..." % tweets_path)
		# Process every line as JSON data
		hashtags = {}
		num_tweets, num_failed, line_number = 0, 0, 0
		num_multiple = 0
		for l in fileinput.input(tweets_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				tweet = json.loads(l)
				tweet_tags = set()
				# find the tags
				if "entities" in tweet:
					if "hashtags" in tweet["entities"] and len(tweet["entities"]["hashtags"]) > 0:
						for tag in tweet["entities"]["hashtags"]:
							tweet_tags.add( "#" + tag["text"].lower().strip() )
				# do not count duplicates
				tweet_tags = list(tweet_tags)
				# process the pairs
				if len(tweet_tags) > 1:
					num_multiple += 1
					for p in itertools.combinations(tweet_tags, 2):
						if p[0] < p[1]:
							pair = frozenset( [p[0],p[1]] )
						else:
							pair = frozenset( [p[1],p[0]] )
						pair_counts[pair] += 1
				num_tweets += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()
		log.info("Processed %d tweets from file" % num_tweets )
		log.info("%d/%d tweets in file contained more than one hashtag" % ( num_multiple, num_tweets ) )
	log.info("Total of %d unique pairs of hashtags" % len(pair_counts) )

	# Output pairs
	log.info("Writing pairs to %s ..." % options.out_path )
	fout = codecs.open( options.out_path, "w", encoding="utf-8", errors="ignore" )
	fout.write("Hashtag1\tHastag2\tCount\n")
	for p in pair_counts:
		pair = list(p)
		pair.sort()
		fout.write( "%s\t%s\t%d\n" % ( pair[0], pair[1], pair_counts[p] )  )
	fout.close()

	# Display top counts
	sx = sorted(pair_counts.items(), key=operator.itemgetter(1), reverse=True)
	log.info("Top %d co-occurring hashtag pairs:" % min( len(sx), options.top ) )
	tab = PrettyTable( ["Hashtag1", "Hashtag2", "Count"] )
	tab.align["Hashtag1"] = "l"
	tab.align["Hashtag2"] = "l"
	tab.align["Count"] = "r"
	for i, p in enumerate(sx):
		if i > options.top:
			break
		pair = list(p[0])
		pair.sort()
		tab.add_row( [pair[0], pair[1], p[1]] )
	log.info(tab)		

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
