#!/usr/bin/env python
"""
A very simple script to export tweets from a JSONL file in CSV format.

Sample usage:
python jsonl-tweet-export.py sample/sample-tweets-500.jsonl -o sample/sample-tweets.csv
"""
import sys, fileinput, codecs, re
from datetime import datetime
from optparse import OptionParser
import logging as log
try:
	import ujson as json 
except:
	import json
from prettytable import PrettyTable

# --------------------------------------------------------------

def parse_twitter_date( s, ignore_time_zones = True ):
	# hack for cases where timezone is not supported by Python strptime 
	if ignore_time_zones:
		parts = s.split(" ")
		smodified =" ".join( parts[0:4] + [ parts[-1] ] )
		return  datetime.strptime(smodified,'%a %b %d %H:%M:%S %Y')
	return datetime.strptime(s,'%a %b %d %H:%M:%S %z %Y')

def fmt_id( x ):
	return '"%s"' % x

def norm( s, sep ):
	s = s.replace(sep, " ")
	return re.sub("\s+", " ", s )

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] json_file1 json_file2 ...")
	parser.add_option("-t", "--top", action="store", type="int", dest="top", help="number of top authors to display", default=10)
	parser.add_option("-o", action="store", type="string", dest="out_path", help="output path for CSV file", default="tweets.csv")
	parser.add_option("-s", action="store", type="string", dest="separator", help="separator character for output file (default is comma)", default=",")
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')
	sep = options.separator

	log.info("Tweets will be written to %s ..." % options.out_path )
	header = ["Tweet_ID", "Created_At", "Author_Screen_Name", "Author_Id", "Text" ]

	fout = codecs.open( options.out_path, "w", encoding="utf-8", errors="ignore" )
	fout.write("%s\n" % sep.join(header) )

	for tweets_path in args:
		log.info("Loading tweets from %s ..." % tweets_path)
		# Process every line as JSON data
		num_tweets, num_failed, line_number = 0, 0, 0
		for l in fileinput.input(tweets_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				tweet = json.loads(l)
				sdate = parse_twitter_date(tweet["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
				values = [ fmt_id(tweet["id"]), sdate, norm(tweet["user"]["screen_name"], sep).lower(), fmt_id(tweet["user"]["id"]), norm(tweet["text"], sep) ]
				fout.write("%s\n" % sep.join(values) )
				num_tweets += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()
		log.info("Wrote %d tweets" % num_tweets )
		fout.flush()

	fout.close()

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
