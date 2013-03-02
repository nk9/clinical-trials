#!/usr/bin/python

import argparse
import trialsDB.trialsDB as db
import os

def main():
	# Handle the arguments
	args = parseArguments()
	
	# Make sure we can create the DB
	dbPath = "trialsDB.sqlite3"
	xmlFilesPath = "study_fields_xml"

	if args.createDB:
		# This is a db population script, so remove the file if it exists
		try:
			os.remove(dbPath)
		except OSError:
			pass
		
		db.create(dbPath, xmlFilesPath, args.startID, args.short)



def parseArguments():
	parser = argparse.ArgumentParser(description='Manage and data mine a clinical trials database')
	parser.add_argument('--create-db', dest='createDB', action='store_true', default=False,
						help='create and initalize the DB file')
	parser.add_argument('--short', dest='short', action='store_true', default=False,
						help='only parse the first 1000 files')
	parser.add_argument('--startID', dest='startID', help='choose an ID to start from')
						
	return parser.parse_args()



# Default function is main()
if __name__ == '__main__':
    main()