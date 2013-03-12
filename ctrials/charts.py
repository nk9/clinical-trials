#!/usr/bin/python

import json
import os
import sys
from . import db
from . import utils


def create(chartsPath, dbPath):
	jsonString = createCharts(loadChartDefs(), dbPath)

	if (len(jsonString)):
		chartsFile = open(chartsPath, 'w')
		chartsFile.write(jsonString)
		chartsFile.close()


def loadChartDefs():
	jsonFile = file(utils.relativePath('charts.json'))
	jsonDict = json.load(jsonFile)
	jsonFile.close()

	chartDefs = {}

	# Have to store the SQL as an array so it's legible in the JSON, but the DB expects a string
	for (chartID, chartDef) in jsonDict.iteritems():
		chartDef["sql"] = " ".join(chartDef["sql"])
		chartDefs[chartID] = chartDef

	return chartDefs

def createCharts(chartDefs, dbPath):
	charts = {}

	try:
		database = db.DBManager(dbPath)
		database.open()

		for (chartID, chartDef) in chartDefs.iteritems():
			chart = Chart(chartID, chartDef, database)
			charts[chart.id] = chart.chartDict()

		database.close()
	except db.DBException as e:
		print e
		sys.exit(1)

	return json.dumps(charts)

class Chart(object):
	def __init__(self, id, definition, db):
		self.db = db

		self.id = id
		self.sql = definition["sql"]
		self.name = definition["name"]
		self.type = definition["type"]
		self.function = definition["function"]
		self.chartJSON = definition["chartJSON"]

	def chartDict(self):
		chartMethod = getattr(self, self.function)
		data = self.fetchData()
		print data
		return chartMethod(data)

	def fetchData(self):
		return self.db.executeAndFetchAll(self.sql)

	def pieChart(self, data):
		chartDict = self.chartJSON

		chartDict['series'][0]['data'] = data

		return chartDict

	def phaseChart(self, data):
		chartDict = self.chartJSON
		newData = []

		phases = {0 : 'None', 1 : '0', 2 : 'I', 4 : 'II', 6 : 'I/II', 8 : 'III', 12 : 'II/III', 16 : 'IV'}

		for (phase, count) in data:
			newData.append([phases[phase], count])

		chartDict['series'][0]['data'] = newData

		return chartDict


	def columnChart(self, data):
		chartDict = self.chartJSON

		columns = zip(*data)

		# First, labels
		chartDict['xAxis']['categories'] = columns[0]

		# Second, all the data
		for (index, col) in enumerate(columns[1:]):
			chartDict['series'][index]['data'] = col

		return chartDict



# Default function is main()
if __name__ == '__main__':
    main()