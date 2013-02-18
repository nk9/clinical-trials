#!/usr/bin/python

import xml.etree.ElementTree as xml
import os, subprocess
import sqlite3
import argparse

def main():
	os.chdir("..")

	# handle the arguments
	args = parseArguments()
	
	# Open the DB
	db = DBManager("db/trialsDB.sqlite3")
	
	# Initalize it if necessary
	if args.createDB:
		db.initalize()
	
	for root, dirs, files in os.walk("study_fields_xml"):
		for index, file in enumerate(files):
			addFileToDB(os.path.join(root, file), db)
	
	db.closeDB()	
				
def parseArguments():
	parser = argparse.ArgumentParser(description='Build a clinical trials database')
	parser.add_argument('--create-db', dest='createDB', action='store_true', default=False,
						help='create and initalize the DB file')
						
	return parser.parse_args()


def runXSLT(path):
	result = subprocess.check_output(["xsltproc", "../process_xml.xslt", path])
	fieldString = result.split("\n")[2] # 0 = XML declaration; 1 = header; 2 = the good stuff
	
	if (len(fieldString)):
		return fieldString.split("\t")
	
def addFileToDB(path, db):
	etree = xml.fromstring(open(path).read())
	
	# Pull out the data
	title = etree.find("brief_title")
	nctID = etree.find("id_info/nct_id")
	sponsor = etree.find("sponsors/lead_sponsor/agency")
	sponsorClass = etree.find("sponsors/lead_sponsor/agency_class")
	status = etree.find("overall_status")
	startDate = etree.find("start_date")
	completionDate = etree.find("completion_date")
	primaryCompletionDate = etree.find("primary_completion_date")
	phase = etree.find("phase")
	
	# Add it to the DB


class DBManager(object):
		def __init__(self, dbPath):
			self.path = dbPath
			self.connection = None
			self.cursor = None
			
			self.openDB()
		
		def openDB(self):
			self.connection = sqlite3.connect(self.path)
			self.cursor = self.connection.cursor()
		
		def initalize(self):
			SQLInit = [line.strip() for line in open('db/SQLInit.txt')]
			
			for step in SQLInit:
				self.cursor.execute(step)
			self.connection.commit()
		
		def closeDB(self):
			self.cursor.close()
            
                
# Default function is main()
if __name__ == '__main__':
    main()
