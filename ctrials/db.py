#!/usr/bin/python

import xml.etree.ElementTree as xml
import os
import sys
from datetime import datetime as dt
import time
import sqlite3
from . import utils


def main():
	create("trialsDB.sqlite3", "trials_xml")

def create(dbPath, xmlFilesPath, startID=None, limit=0):
	# Remove the database file if it already exists
	try:
		os.remove(dbPath)
	except OSError:
		pass

	# Create the database file anew
	try:
		db = DBManager(dbPath)
		db.openDB(initalize=True)
	except DBException as e:
		print e
		sys.exit(1)

	# Iteration state
	skipFile = (startID is not None)
	numberParsed = 0

	# Walk through the xml files and add them to the DB
	for root, dirs, files in os.walk(xmlFilesPath):

		for file in files:
			if limit > 0 and numberParsed > limit:
				break

			if skipFile and file.startswith(startID):
				skipFile = False

			if not skipFile:
				trial = Trial(os.path.join(root, file))
				trial.populate()
				
				db.addTrial(trial)
				numberParsed += 1
	
	db.commitTrials()
	db.closeDB()




###
# DBManager
###

class DBException(Exception):
	pass

class DBManager(object):
	def __init__(self, dbPath):
		####
		# Current user_version of the SQL database
		####
		self.user_version = 1

		self.path = dbPath
		self.connection = None
		self.cursor = None
		self.prayleACTs = None
		self.currentNCTID = ""


	def openDB(self, initalize=False):
		self.connection = sqlite3.connect(self.path)
		self.cursor = self.connection.cursor()
		self.cursor.execute('PRAGMA foreign_keys = ON;')

		if initalize:
			self.initalize()
		else:
			# Check the database's version
			self.cursor.execute('PRAGMA user_version;')
			version = self.cursor.fetchone()[0]

			if version != self.user_version:
				raise DBException("Error opening database file: versions don't match",
								  {'script version' : self.user_version, 'database version' : version })
	

	def initalize(self):
		SQLInit = open(utils.relativePath('db_init.sql')).read()
		
		self.cursor.execute('PRAGMA user_version = %d;' % self.user_version)
		self.cursor.executescript(SQLInit)
		
		self.connection.commit()
	

	def closeDB(self):
		self.cursor.close()
	

	def addTrial(self, trial):
		if trial.isComplete():
			self.currentNCTID = trial.nctID
			
			sponsorClassID = self.insertSponsorClass(trial)
			sponsorID = self.insertSponsor(trial, sponsorClassID)
			countryIDs = self.insertCountries(trial)

			trialID = self.insertTrial(trial, sponsorID)

			self.insertTrialCountries(trialID, countryIDs)
			self.insertInterventions(trial, trialID)
	

	def sqlDate(self, date):
		outDate = 0

		if date is not None:
			try:
				outDate = time.strftime('%Y-%m-%d %H:%M:%S', date.timetuple())
			except Exception as e:
				print "%s: failed converting date '%s'" % (self.currentNCTID, date)

		return outDate


	def insertSponsorClass(self, trial):
		self.cursor.execute('INSERT OR IGNORE INTO sponsorClasses (class) VALUES(?)', (trial.sponsorClass,))
		self.cursor.execute('SELECT id FROM sponsorClasses WHERE class = ?', (trial.sponsorClass,))
		
		return self.cursor.fetchone()[0]
	

	def insertSponsor(self, trial, sponsorClassID):
		self.cursor.execute('INSERT OR IGNORE INTO sponsors (name, class_id) VALUES(?, ?)', (trial.leadSponsor, sponsorClassID))
		self.cursor.execute('SELECT id FROM sponsors WHERE name = ?', (trial.leadSponsor,))
		
		return self.cursor.fetchone()[0]

	def insertCountries(self, trial):
		countryIDs = []

		for country in trial.countries:
			self.cursor.execute('INSERT OR IGNORE INTO countries (name) VALUES(?)', (country,))
			self.cursor.execute('SELECT id FROM countries WHERE name = ?', (country,))
			
			countryIDs.append(self.cursor.fetchone()[0])

		return countryIDs


	def insertTrial(self, trial, sponsorID):
		columns = [	'sponsor_id', 'title', 'nctID', 'status', 'phaseMask', 'startDate',
					'completionDate', 'primaryCompletionDate', 'resultsDate', 'includedInPrayle']
		sqlString = 'INSERT INTO trials ({0}) VALUES ({1})'.format(','.join(columns), ','.join(['?']*len(columns)))

		self.cursor.execute(sqlString,
							(sponsorID,
							 trial.title,
							 trial.nctID,
							 trial.recruitment,
							 trial.phaseMask,
							 self.sqlDate(trial.startDate),
                             self.sqlDate(trial.completionDate),
                             self.sqlDate(trial.primaryCompletionDate),
                             self.sqlDate(trial.resultsDate),
                             self.trialIncludedInPrayle(trial)))
		self.cursor.execute('SELECT id FROM trials WHERE nctID = ?', (trial.nctID,))

		return self.cursor.fetchone()[0]


	def insertTrialCountries(self, trialID, countryIDs):
		for countryID in countryIDs:
			self.cursor.execute('INSERT INTO trialCountries (trial_id, country_id) VALUES(?,?)', (trialID, countryID))


	def insertInterventions(self, trial, trialID):
		for iDict in trial.interventions:
			# First, insert the type into the types table
			self.cursor.execute('INSERT OR IGNORE INTO interventionTypes (type) VALUES(?)', (iDict["type"],))
			self.cursor.execute('SELECT id FROM interventionTypes WHERE type = ?', (iDict["type"],))
			typeID = self.cursor.fetchone()[0]

			# Then, add the intervention itself to the interventions table
			self.cursor.execute('INSERT INTO interventions (trial_id, type_id, name) VALUES(?,?,?)', (trialID, typeID, iDict["name"]))

	
	def commitTrials(self):
		self.connection.commit()


	def trialIncludedInPrayle(self, trial):
		if self.prayleACTs is None:
			praylePath = utils.relativePath('Prayle2012ACTs.txt')
			self.prayleACTs = [line.strip() for line in open(praylePath)]

		if trial.nctID in self.prayleACTs:
			return 1
		else:
			return 0


	def runQuery(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()
        


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
		self.nctID = os.path.splitext(os.path.basename(path))[0]
		self.leadSponsor = ""
		self.sponsorClass = ""
		self.recruitment = ""
		self.interventions = []
		self.startDate = ''
		self.completionDate = ''
		self.primaryCompletionDate = ''
		self.resultsDate = ''
		self.phaseMask = 0
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
		self.phaseMask = self.parsePhaseMask(etree.find("phase").text)
		
		for e in etree.findall("location_countries/country"):
			self.countries.append(e.text)

		for e in etree.findall("intervention"):
			interventionDict = {'type': e.find("intervention_type").text,
								'name': e.find("intervention_name").text}
			self.interventions.append(interventionDict)

		# Dates
		self.startDate = self.parseDate(etree.find("start_date"))
		self.completionDate = self.parseDate(etree.find("completion_date"))
		self.primaryCompletionDate = self.parseDate(etree.find("primary_completion_date"))
		self.resultsDate = self.parseDate(etree.find("firstreceived_results_date"))



	def isComplete(self):
		"""This will probably contain more checks"""
		return	self.startDate is not None
	
	
	
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
					print "Failed parsing date for %s, '%s': %s" % (self.nctID, stringToParse, e)
		
		return outDate
	
	def parsePhaseMask(self, phaseText):
		outMask = 0
		
		if "0" in phaseText:
			outMask += 1 << 0
		if "1" in phaseText:
			outMask += 1 << 1
		if "2" in phaseText:
			outMask += 1 << 2
		if "3" in phaseText:
			outMask += 1 << 3
		if "4" in phaseText:
			outMask += 1 << 4
		
		return outMask
	
                
# Default function is main()
if __name__ == '__main__':
    main()
