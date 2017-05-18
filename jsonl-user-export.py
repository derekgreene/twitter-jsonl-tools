#!/usr/bin/env python
"""
A very simple script to export user metadata from a JSONL file in CSV format.

Sample usage:
python jsonl-user-export.py sample/sample-users-50.jsonl -o sample/sample-users.csv
"""
import sys, fileinput, codecs, re
from datetime import datetime
from optparse import OptionParser
import logging as log
try:
	import ujson as json 
except:
	import json

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
	if s is None or len(s) == 0:
		return ""
	s = s.replace(sep, " ")
	return re.sub("\s+", " ", s ).strip()

# --------------------------------------------------------------

def main():
	parser = OptionParser(usage="usage: %prog [options] json_file1 json_file2 ...")
	parser.add_option("-t", "--top", action="store", type="int", dest="top", help="number of top authors to display", default=10)
	parser.add_option("-o", action="store", type="string", dest="out_path", help="output path for CSV file", default="users.csv")
	parser.add_option("-s", action="store", type="string", dest="separator", help="separator character for output file (default is comma)", default=",")
	(options, args) = parser.parse_args()	
	if( len(args) < 1 ):
		parser.error( "Must specify at least one JSONL file" )
	log.basicConfig(level=20, format='%(message)s')
	sep = options.separator

	log.info("Tweets will be written to %s ..." % options.out_path )
	header = ["User_ID", "Screen_Name", "Name", "Followers_count", "Friends_Count", "Tweets_Count", "Created_At", "Language", "Location", "Description" ]

	fout = codecs.open( options.out_path, "w", encoding="utf-8", errors="ignore" )
	fout.write("%s\n" % sep.join(header) )

	for users_path in args:
		log.info("Loading user metadata from %s ..." % users_path)
		# Process every line as JSON data
		num_users, num_failed, line_number = 0, 0, 0
		for l in fileinput.input(users_path):
			l = l.strip()
			if len(l) == 0:
				continue
			try:
				line_number += 1
				user = json.loads(l)
				values = [ fmt_id(user["id"]), norm(user["screen_name"],sep).lower(), norm(user["name"],sep) ]
				sdate = parse_twitter_date(user["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
				values += [ str(user["followers_count"]), str(user["friends_count"]), str(user["statuses_count"]), sdate ]
				values += [ norm(user["lang"],sep), norm(user["location"],sep), norm(user["description"],sep) ]
				fout.write("%s\n" % sep.join(values) )
				num_users += 1
				if line_number % 50000 == 0:
					log.info("Processed %d lines" % line_number)
			except Exception as e:
				log.error("Failed to parse tweet on line %d: %s" % ( line_number, e ) )
				num_failed += 1
		fileinput.close()
		log.info("Wrote %d users" % num_users )
		fout.flush()

	fout.close()

# --------------------------------------------------------------

if __name__ == "__main__":
	main()
