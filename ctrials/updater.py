#!/usr/bin/python

import db as db
from zipfile import ZipFile
from StringIO import StringIO
from Queue import Queue, PriorityQueue
import threading
import datetime as dt
from clinical_trials_python.clinical_trials import Trials
import os


class Updater(object):
	def __init__(self, dbPath):
		self.dbPath = dbPath
		
		self.update()

	def update(self):
		#Queues to manage downloading
		dateQ = Queue(0)
		xmlTrialQ = PriorityQueue(100)

		# Create the single SQLAlchemy thread to update DB records
		sqlaThread = threading.Thread(target=self.updateTrials, args=(dateQ, xmlTrialQ))
		sqlaThread.daemon = True
		sqlaThread.start()

		# TODO: Fetch the real start date
		# startDate = dt.date(2013, 03, 15)
		startDate = dt.date(2013,12, 18)
		delta = dt.date.today() - startDate
		dateList = [startDate + dt.timedelta(days=x) for x in range(0, delta.days)]

		print dateList

		# Add relevant dates to the list to be fetched
		for currentDate in dateList:
			dateQ.put(currentDate)

		print dateQ.queue

		numWorkerThreads = min(10, dateQ.qsize())

		# Create n worker threads to fetch the zip files of updated content and produce xmlTrial objects
		for i in range(numWorkerThreads):
			t = threading.Thread(target=self.fetchUpdatedTrials, args=(dateQ, xmlTrialQ))
			t.daemon = True
			t.start()

		dateQ.join() 	 # block until all dates have been fetched
		xmlTrialQ.join() # block until all xmlTrials have been created


	def fetchUpdatedTrials(self, dateQ, xmlTrialQ):
		print "-fetchUpdatedTrials"
		keepFetching = True

		while keepFetching:
			currentDate = dateQ.get()
			dateString = currentDate.strftime('%m/%d/%Y')
			print "fetching date: %s" % dateString
			trialDownloader = Trials()
			zipfile = None

			try:
				data = trialDownloader.download(lastUpdatedStart=dateString, lastUpdatedEnd=dateString)
			except Exception as e:
				print "Trial download failed! Date: %s" % currentDate
				print e
				keepFetching = False
				continue

			if len(data) == 0:
				print "No trials for %s" % dateString
			else:
				try:
					zipfile = ZipFile(StringIO(data))
				except Exception as e:
					print "Failed unzipping file for date: %s" % currentDate
					print e
					print "Data length: %d" % len(data)
					keepFetching = False
					continue

				for name in zipfile.namelist():
					print "-name: %s date: %s" % (name, currentDate)
					itemNumber = 0
					nctID = os.path.splitext(name)[0]
					data = zipfile.read(name)
					xmlTrial = db.XMLTrial(data, nctID)
					xmlTrial.populate()
					xmlTrialQ.put((currentDate, xmlTrial))
					itemNumber += 1

			dateQ.task_done()


	def updateTrials(self, dateQ, xmlTrialQ):
		print "=updateTrials"
		try:
			database = db.DBManager(self.dbPath, mutable=True)
			database.open()
		except db.DBException as e:
			print e
			sys.exit(1)

		pass # Code below is untested as yet...

		importer = db.TrialImporter(database)
		first = True
		threadName = threading.current_thread().name

		print "=importer created %d %d %s" % (first, xmlTrialQ.qsize(), threadName)

		while first or not dateQ.empty() or not xmlTrialQ.empty():
			print "=will insert trial %s" % (threadName)
			(sortNumber, xmlTrial) = xmlTrialQ.get()
			importer.updateTrial(xmlTrial)
			print "=inserted %s %s" % (xmlTrial.nctID, threadName)
			xmlTrialQ.task_done()
			first = False
			print "=xmlTrialQ size=%d dateQ size=%d" % (xmlTrialQ.qsize(), dateQ.qsize())

		importer.commitTrials()
		database.close()


# Default function is main()
if __name__ == '__main__':
	main()