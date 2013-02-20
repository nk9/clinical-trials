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
		self.cursor.execute('PRAGMA foreign_keys = ON;')
	
	def initalize(self):
		SQLInit = open('db/SQLInit.txt').read()
		
		self.cursor.executescript(SQLInit)
		
		self.connection.commit()
	
	def closeDB(self):
		self.cursor.close()
	
	def addTrial(self, trial):
		print trial.id
		
		# Insert countries where appropriate
		for country in trial.countries:
			self.cursor.execute('INSERT OR IGNORE INTO countries (name) VALUES(?)', (country,))
	
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
		self.countries = []
		self.title = ""
	
	
	
	def populate(self):
		self.parseXML()
	
	
	###
	# Getting the data and parsing it
	###
	def parseXML(self):
		etree = xml.fromstring(open(self.path).read())

		# Pull out the data
		self.title = etree.find("brief_title").text
		self.leadSponsor = etree.find("sponsors/lead_sponsor/agency").text
		self.sponsorClass = etree.find("sponsors/lead_sponsor/agency_class").text
		self.recruitment = etree.find("overall_status").text
		self.phase = etree.find("phase").text
		
		for e in etree.findall("location_countries/country"):
			self.countries.append(e.text)

		# Dates
		self.startDate = self.parseDate(etree.find("start_date"))
		self.completionDate = self.parseDate(etree.find("completion_date"))
		self.primaryCompletionDate = self.parseDate(etree.find("primary_completion_date"))
		self.resultsDate = self.parseDate(etree.find("firstreceived_results_date"))
	
	
	
	def parseDate(self, date):
		stringToParse = ''
# 		outDate = datetime.date(datetime.MINYEAR, 1, 1) # MINYEAR = invalid date
		outDate = None
		
		if isinstance(date, xml.Element):
			stringToParse = date.text
		elif isinstance(date, str):
			stringToParse = date
		
		if len(stringToParse):
			try:
				outDate = dt.strptime(stringToParse, '%B %d, %Y').date()
			except Exception as e:
				try:
					outDate = dt.strptime(stringToParse, '%B %Y').date()
				except Exception as e:
					print "Failed parsing date for %s, '%s': %s" % (self.id, stringToParse, e)
		
		return outDate
	
	
                
# Default function is main()
if __name__ == '__main__':
    main()
