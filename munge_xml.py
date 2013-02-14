#!/usr/bin/python

import os, os.path, subprocess
from datetime import datetime as dt
import datetime

def main():
	for root, _, files in os.walk("study_fields_xml"):
		for index, file in enumerate(files):
			fullpath = os.path.join(root, file)
			
			trial = Trial(fullpath)
			if index == 0:
				print trial.outputHeader()

# 			print trial.outputLine()
			if trial.isACT() and trial.includedInPrayle():
				print trial.outputLine()
		
		print "\n" # end the file with a newline


class Trial(object):
	def __init__(self, path):
		self.path = path
		self.fields = []
		
		# Header fields
		self.headerFields = ['NCT ID', 'Source', 'Recruitment', 'Interventions',
							 'Start Date', 'Completion Date', 'Primary Completion Date',
							 'Phase', 'Countries']
		
		# Field variables
		self.id = ""
		self.source = ""
		self.recruitment = ""
		self.interventions = ""
		self.startDate = None
		self.completionDate = None
		self.primaryCompletionDate = None
		self.phase = ""
		self.countries = ""
		
		# Run!
		self.runXSLT()
		self.processFields()
	
	
	
	###
	# Getting the data and parsing it
	###
	def runXSLT(self):
		result = subprocess.check_output(["xsltproc", "process_xml.xslt", self.path])
		fieldString = result.split("\n")[2] # 0 = XML declaration; 1 = header; 2 = the good stuff
		
		if (len(fieldString)):
			self.fields = fieldString.split("\t")
	
	
	
	def processFields(self):
		# R is going to need 3-part dates, but the XML doesn't include a day. Sometimes.
		# So we have to guess.
		self.id = self.fields[0]
		self.source = self.fields[1]
		self.recruitment = self.fields[2]
		self.interventions = self.fields[3]
		self.startDate = self.parseDate(self.fields[4])
		self.completionDate = self.parseDate(self.fields[5])
		self.primaryCompletionDate = self.parseDate(self.fields[6])
		self.phase = self.fields[7]
		self.countries = self.fields[8]
	
	
	
	def parseDate(self, dateString):
		outDate = datetime.date(datetime.MINYEAR, 1, 1) # MINYEAR = invalid date
		
		if len(dateString):
			try:
				outDate = dt.strptime(dateString, '%B %d, %Y').date()
			except Exception as e:
				try:
					outDate = dt.strptime(dateString, '%B %Y').date()
				except Exception as e:
					print "Failed parsing date for %s, '%s': %s" % (self.id, dateString, e)
		
		return outDate
	
	
	
	###
	# Calculating whether the FDAAA applies to the trial (ACT = Applicable Clinical Trial)
	###
	
	def isACT(self):
		return self.meetsDateRequirements() and \
			   self.isPhase2Plus() and \
			   self.tookPlaceInTheUS() and \
			   self.hasApplicableIntervention()
	
	def meetsDateRequirements(self):
		initiationCutoff = datetime.date(2007, 9, 27)
		ongoingCutoff = datetime.date(2007, 12, 26)
		invalidDate	= datetime.date(datetime.MINYEAR, 1, 1) 
		
		initiationApplies = self.startDate > initiationCutoff
		completionApplies = (self.completionDate >= ongoingCutoff or
							 self.primaryCompletionDate >= ongoingCutoff)
		noStartDate		  = self.startDate == invalidDate
		noCompletionDate  = (self.completionDate == invalidDate and \
							 self.primaryCompletionDate == invalidDate)
		
		return initiationApplies or (not noStartDate and (noCompletionDate or completionApplies))
	
	def isPhase2Plus(self):
		return not (self.phase == "Phase 0" or self.phase == "Phase 1")
	
	def tookPlaceInTheUS(self):
		return "United States" in self.countries
	
	def hasApplicableIntervention(self):
		return any(x in self.interventions for x in ["Drug", "Biological", "Device"])
	
	
	
	###
	# And Prayle
	###
	
	def includedInPrayle(self):
		return self.primaryCompletionDate >= datetime.date(2009, 01, 01) and \
			   self.primaryCompletionDate <  datetime.date(2010, 01, 01)
	
	
	
	###
	# Calculating how much the trial owes
	###
	
	def fine(self):
		return 10000


	
	###
	# Output
	###
	def outputHeader(self):
		return "\t".join(self.headerFields)
	
	def outputLine(self):
		return "\t".join(self.fields)

# Default function is main()
if __name__ == '__main__':
	main()
