#!/usr/bin/python

import json
import os
from . import db

def create(chartsPath):
	db.foo()
	jsonString = createCharts(loadChartDefs())

	if (len(jsonString)):
		chartsFile = open(chartsPath, 'w')
		chartsFile.write(jsonString)
		chartsFile.close()


def loadChartDefs():
	module_dir, module_file = os.path.split(__file__)
	jsonFile = file(os.path.join(module_dir, 'charts.json'))
	jsonList = json.load(jsonFile)
	jsonFile.close()

	chartDefs = []

	# Have to store the SQL as an array so it's legible in the JSON, but the DB expects a string
	for chartDef in jsonList:
		chartDef["sql"] = " ".join(chartDef["sql"])
		chartDefs.append(chartDef)

	return chartDefs

def createCharts(chartDefs):
	charts = {}

	for chartDef in chartDefs:
		chart = Chart(chartDef)
		charts[chart.id] = chart.chartDict()

	return json.dumps(charts)

class Chart(object):
	def __init__(self, definition):
		self.id = definition["id"]
		self.sql = definition["sql"]
		self.name = definition["name"]
		self.type = definition["type"]
		self.chartJSON = definition["chartJSON"]

	def chartDict(self):
		chartMethod = getattr(self, self.type + "Chart")
		return chartMethod()

	def pieChart(self):
		chartDict = self.chartJSON
		
		data = chartDict['series'][0]['data']
		data[0] = ["Industry", 0.4]
		data[1] = ["NIH", 0.1]

		chartDict['series'][0]['data'] = data

		return chartDict


# Default function is main()
if __name__ == '__main__':
    main()