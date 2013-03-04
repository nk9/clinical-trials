#!/usr/bin/python

import argparse
import ctrials.db as db
import ctrials.charts as charts
import os

def main():
	# Handle the arguments
	args = parseArguments()
	dbPath = None

	# Create the database if requested
	if args.createDB:
		if args.xmlFilesPath is None:
			print "If you're going to create a database, you must pass in the path to the XML files directory"
			return 0
		else:
			dbPath =  db.create(args.dbPath, args.xmlFilesPath, args.startID, args.limit)

	# Create the charts
	chartsPath = "web/js/charts.json"
	if args.chartsPath is not None:
		chartsPath = args.chartsPath

	charts.create(chartsPath, args.dbPath)




def parseArguments():
	parser = argparse.ArgumentParser(description='Manage and data mine a clinical trials database')
	parser.add_argument('--createDB', dest='createDB', action='store_true', default=False,
						help='Create and initalize the DB file using the path provided')
	parser.add_argument('--xmlFilesPath', dest='xmlFilesPath',
						help='A directory of trials in ClinicalTrials.gov\'s XML format')
	parser.add_argument('--chartsPath', dest='chartsPath',
						help='Choose a destination for the JSON file describing the charts; defaults to "web/js/charts.json"')
	parser.add_argument('--limit', dest='limit', type=int,
						help='Set a limit on the number of files from the XML path to be included')
	parser.add_argument('--startID', dest='startID', help='Choose an NCT ID to start from')
	parser.add_argument('dbPath', default='trialsDB.sqlite3',
						help='The path to the trials database file, either to be created or already there')
						
	return parser.parse_args()



# Default function is main()
if __name__ == '__main__':
    main()