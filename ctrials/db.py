#!/usr/bin/python

import xml.etree.ElementTree as xml
from datetime import datetime as dt
import os, sys, time, re
import sqlite3
import json

from . import utils
from model import *

#SQLAlchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import ClauseElement


def main():
	create("trialsDB.sqlite3", "trials_xml")

def create(dbPath, xmlFilesPath, startNumber, limit=0):
	# Remove the database file if it already exists
	try:
		os.remove(dbPath)
	except OSError:
		pass

	# Create the database file anew
	try:
		db = DBManager(dbPath)
		db.open(initalize=True)
	except DBException as e:
		print e
		sys.exit(1)

	# Iteration state
	skipFile = (startNumber > 0)
	numberParsed = 0
	idNumRE = re.compile('NCT0*(\d*).xml')

	importer = TrialImporter(db)

	# Walk through the xml files and add them to the DB
	for root, dirs, files in os.walk(xmlFilesPath):

		for filename in files:
			if not filename.endswith('xml'):
				continue

			if limit > 0 and numberParsed > limit:
				break

			if skipFile:
				m = idNumRE.match(filename)
				thisID = 0

				if m:
					thisID = int(m.group(1))

				if thisID >= startNumber:
					skipFile = False

			if not skipFile:
				trial = XMLTrial(os.path.join(root, filename))
				trial.populate()
				
				importer.addTrial(trial)
				numberParsed += 1
	
	importer.commitTrials()
	db.close(setVersion=True)




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
		self.user_version = 3

		self.path = dbPath
		self.engine = None
		self.session = None


	def open(self, initalize=False):
		if not initalize:
			self.checkVersion()

		URL = 'sqlite:///%s' % self.path
		self.engine = create_engine(URL, echo=False)
		event.listen(self.engine, 'connect', self.pragmaOnConnect)
		sessionMaker = sessionmaker(bind=self.engine)
		self.session = sessionMaker()

		if initalize:
			self.initalize()


	def pragmaOnConnect(self, dbapi_con, con_record):
		dbapi_con.execute('pragma foreign_keys=ON')

	def initalize(self):
		Base.metadata.create_all(self.engine)


	def checkVersion(self):
		connection = sqlite3.connect(self.path)
		cursor = connection.cursor()
		cursor.execute('PRAGMA user_version;')
		version = cursor.fetchone()[0]
		cursor.close()

		if version != self.user_version:
			raise DBException("Error opening database file: versions don't match",
							  {'script version' : self.user_version, 'database version' : version })


	def setVersion(self):
		connection = sqlite3.connect(self.path)
		cursor = connection.cursor()
		cursor.execute('PRAGMA user_version = %d;' % self.user_version)
		cursor.close()


	def getOrCreate(self, model, defaults=None, **kwargs):
		instance = self.session.query(model).filter_by(**kwargs).first()

		if instance:
			return instance	#, False
		else:
			params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
			instance = model(**params)
			self.session.add(instance)
			return instance	#, True


	def commitContent(self):
		self.session.commit()


	def close(self, setVersion=False):
		self.session.close()

		if setVersion:
			self.setVersion()








###
# TrialImporter
###

class TrialImporter(object):
	def __init__(self, dbManager):
		self.db = dbManager
		self.prayleACTs = None
		self.currentNCTID = ""
		self.parensRE = re.compile(".*\(([^\)]+)\).*")

		shortNamesFile = open(utils.relativePath('sponsorShortNames.json'))
		self.sponsorShortNames = json.load(shortNamesFile)
		shortNamesFile.close()


	def addTrial(self, xmlTrial):
		if xmlTrial.isComplete():
			self.currentNCTID = xmlTrial.nctID
			print "will add trial: %s" % self.currentNCTID

			sponsorClass = self.insertSponsorClass(xmlTrial)
			sponsor = self.insertSponsor(xmlTrial, sponsorClass)
			countries = self.insertCountries(xmlTrial)
			interventions = self.insertInterventions(xmlTrial)

			trial = self.insertTrial(xmlTrial, sponsor, countries, interventions)
	

	def sqlDate(self, date):
		outDate = 0

		if date is not None:
			try:
				outDate = time.strftime('%Y-%m-%d %H:%M:%S', date.timetuple())
			except Exception as e:
				print "%s: failed converting date '%s'" % (self.currentNCTID, date)

		return outDate


	def insertSponsorClass(self, trial):
		return self.db.getOrCreate(SponsorClass, sclass=trial.sponsorClass)
	

	def insertSponsor(self, trial, sponsorClass):
		name = trial.leadSponsor
		shortName = None

		if name in self.sponsorShortNames:
			shortName = self.sponsorShortNames[name]

		# Pull out the shortname if needed, and if available
		if shortName is None and "(" in name:
			m = self.parensRE.match(name)

			if m:
				shortName = m.groups()[0]

		return self.db.getOrCreate(Sponsor, name=name, shortName=shortName, sclass=sponsorClass)


	def insertCountries(self, trial):
		outCountries = []
		for country in trial.countries:
			outCountries.append(self.db.getOrCreate(Country, name=country))

		return outCountries


	def insertTrial(self, xmlTrial, sponsor, countries, interventions):
		trial = Trial(xmlTrial.nctID)
		trial.countries = countries
		trial.sponsor = sponsor
		trial.interventions = interventions

		for col in trial.domesticKeys:
			value = getattr(xmlTrial, col, None)

			if value:
				setattr(trial, col, value)

		self.db.session.add(trial)
		return trial


	def insertInterventions(self, xmlTrial):
		interventions = []

		for iDict in xmlTrial.interventions:
			itype = self.db.getOrCreate(InterventionType, itype=iDict["type"])
			intervention = Intervention(iDict["name"], itype)
			interventions.append(intervention)

			self.db.session.add(intervention)

		return interventions

	
	def commitTrials(self):
		self.db.commitContent()


	def trialIncludedInPrayle(self, trial):
		if self.prayleACTs is None:
			praylePath = utils.relativePath('Prayle2012ACTs.txt')
			self.prayleACTs = [line.strip() for line in open(praylePath)]

		if trial.nctID in self.prayleACTs:
			return 1
		else:
			return 0
		


###
# XMLTrial
###

class XMLTrial(object):
	def __init__(self, path):
		self.path = path
		self.fields = []
		
		# Header fields
		# self.headerFields = ['NCT ID', 'Lead Sponsor', 'Sponsor Class', 'Recruitment', 'Interventions',
		# 					 'Start Date', 'Completion Date', 'Primary Completion Date', 'Results Date',
		# 					 'Phase', 'Countries']
		
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
