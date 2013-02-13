#!/usr/bin/python

import os, os.path, subprocess
from datetime import datetime
def main():
	for root, _, files in os.walk("study_fields_xml"):
		for index, file in enumerate(files):
			fullpath = os.path.join(root, file)
			
			doc = CTXMLDoc(fullpath)
			if index == 0:
				print doc.outputHeader()

			print doc.outputLine()
		
		print "\n" # end the file with a newline


class CTXMLDoc(object):
	def __init__(self, path):
		self.path = path
		self.fields = []
		self.headerFields = ['NCT ID', 'Source', 'Recruitment', 'Interventions',
							 'Start Date', 'Completion Date', 'Primary Completion Date',
							 'Phase', 'Countries']
		
		# Run!
		self.runXSLT()
		self.processFields()
	
	def id(self):
		return self.fields[0]
	
	def processFields(self):
		# R is going to need 3-part dates, but the XML doesn't include a day. Sometimes.
		# So we have to guess.
		self.fields[4] = self.parseDate(self.fields[4])
		self.fields[5] = self.parseDate(self.fields[5])
		self.fields[6] = self.parseDate(self.fields[6])
	
	def parseDate(self, dateString):
		outDateString = ""
		
		if len(dateString):
			try:
				outDate = datetime.strptime(dateString, '%B %d, %Y')
			except Exception as e:
				try:
					outDate = datetime.strptime(dateString, '%B %Y')
				except Exception as e:
					print "Failed parsing Start Date for %s: '%s'" % (self.id(), dateString)
			
			outDateString = datetime.strftime(outDate, '%d/%m/%Y')
		
		return outDateString
	
	def runXSLT(self):
		result = subprocess.check_output(["xsltproc", "process_xml.xslt", self.path])
		fieldString = result.split("\n")[2] # 0 = XML declaration; 1 = header; 2 = the good stuff
		
		if (len(fieldString)):
			self.fields = fieldString.split("\t")
		
	def outputHeader(self):
		return "\t".join(self.headerFields)
	
	def outputLine(self):
		return "\t".join(self.fields)

# Default function is main()
if __name__ == '__main__':
	main()

