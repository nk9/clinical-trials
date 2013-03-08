#!/usr/bin/python

import json
import os
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
	jsonList = json.load(jsonFile)
	jsonFile.close()

	chartDefs = {}

	# Have to store the SQL as an array so it's legible in the JSON, but the DB expects a string
	for (chartID, chartDef) in jsonList.iteritems():
		chartDef["sql"] = " ".join(chartDef["sql"])
		chartDefs[chartID] = chartDef

	return chartDefs

def createCharts(chartDefs, dbPath):
	charts = {}

	for (chartID, chartDef) in chartDefs.iteritems():
		database = db.DBManager(dbPath)
		chart = Chart(chartID, chartDef, database)
		charts[chart.id] = chart.chartDict()
		database.closeDB()

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
		return chartMethod(data)

	def fetchData(self):
		return self.db.runQuery(self.sql)

	def pieChart(self, data):
		print data
		chartDict = self.chartJSON

		# chartDict['series'][0]['data'] = chartData
		chartDict['series'][0]['data'] = data

		return chartDict

	def timeSeriesColumnChart(self, data):
		chartDict = self.chartJSON
		print data
		years = []
		completedUnreported = []
		reported = []

		# Split out the data as it's needed by the charts API
		for t in data:
			years.append(t[0])
			completedUnreported.append(t[1])
			reported.append(t[2])

		chartDict['xAxis']['categories'] = years
		chartDict['series'][0]['data'] = completedUnreported
		chartDict['series'][1]['data'] = reported

		return chartDict



# Default function is main()
if __name__ == '__main__':
    main()