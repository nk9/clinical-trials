#!/usr/bin/python

import xml.etree.ElementTree as xml
import os, subprocess
from datetime import datetime as dt
import datetime, calendar
import sqlite3
import argparse

def main():
	os.chdir("..")

	# Handle the arguments
	args = parseArguments()
	
	# Make sure we can create the DB
	dbpath = "db/trialsDB.sqlite3"
	
	# This is a db population script, so remove the file if it exists
	try:
		os.remove(dbpath)
	except OSError:
		pass
	
	# Create the DB
	db = DBManager(dbpath)
	db.initalize()
	
	# Walk through the xml files and add them to the DB
	for root, dirs, files in os.walk("study_fields_xml"):
		for index, file in enumerate(files):
			if index > 1000 and args.short:
				break
			
			trial = Trial(os.path.join(root, file))
			trial.populate()
			
			db.addTrial(trial)
	
	db.commitTrials()
	db.closeDB()	



def parseArguments():
	parser = argparse.ArgumentParser(description='Build a clinical trials database')
	parser.add_argument('--create-db', dest='createDB', action='store_true', default=False,
						help='create and initalize the DB file')
	parser.add_argument('--short', dest='short', action='store_true', default=False,
						help='only parse the first 1000 files')
						
	return parser.parse_args()
	



###
# DBManager
###

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
	
	def addTrial(self, trial):
		print trial.id
		self.cursor.execute('INSERT INTO sponsorClasses (class) VALUES(?)', (trial.id,))
	
	def commitTrials(self):
		self.connection.commit()
        


###
# Trial
###

class Trial(object):
	def __init__(self, path):
		self.path = path
		self.fields = []
		
		# Header fields
		self.headerFields = ['NCT ID', 'Lead Sponsor', 'Sponsor Class', 'Recruitment', 'Interventions',
							 'Start Date', 'Completion Date', 'Primary Completion Date', 'Results Date',
							 'Phase', 'Countries']
		
		# Field variables
		self.id = os.path.splitext(os.path.basename(path))[0]
		self.leadSponsor = ""
		self.sponsorClass = ""
		self.recruitment = ""
		self.interventions = ""
		self.startDate = ''
		self.completionDate = ''
		self.primaryCompletionDate = ''
		self.resultsDate = ''
		self.phase = ""
		self.countries = ""
		self.title = ""
	
	
	
	def populate(self):
		self.parseXML()
		self.processFields()
	
	
	###
	# Getting the data and parsing it
	###
	def parseXML(self):
		etree = xml.fromstring(open(self.path).read())

		# Pull out the data
		self.title = etree.find("brief_title")
		self.leadSponsor = etree.find("sponsors/lead_sponsor/agency")
		self.sponsorClass = etree.find("sponsors/lead_sponsor/agency_class")
		self.recruitment = etree.find("overall_status")
		self.startDate = etree.find("start_date")
		self.completionDate = etree.find("completion_date")
		self.primaryCompletionDate = etree.find("primary_completion_date")
		self.phase = etree.find("phase")
	
	
	
	def processFields(self):
		# Date munging
		self.startDate = self.parseDate(self.startDate)
		self.completionDate = self.parseDate(self.completionDate)
		self.primaryCompletionDate = self.parseDate(self.primaryCompletionDate)
# 		self.resultsDate = self.parseDate(self.resultsDate)
	
	
	
	def parseDate(self, dateString):
		outDate = datetime.date(datetime.MINYEAR, 1, 1) # MINYEAR = invalid date
		
		if dateString != None and len(dateString):
			try:
				outDate = dt.strptime(dateString, '%B %d, %Y').date()
			except Exception as e:
				try:
					outDate = dt.strptime(dateString, '%B %Y').date()
				except Exception as e:
					print "Failed parsing date for %s, '%s': %s" % (self.id, dateString, e)
		
		return outDate

                
# Default function is main()
if __name__ == '__main__':
    main()
