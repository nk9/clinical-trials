#!/usr/bin/python

import json
import os

def create(chartsPath):
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
	JSONCharts = {}

	for chartDef in chartDefs:
		chart = Chart(chartDef)
		JSONCharts[chart.id] = chart.JSONChart()

	return json.dumps(JSONCharts)

class Chart(object):
	def __init__(self, definition):
		self.id = definition["id"]
		self.sql = definition["sql"]
		self.name = definition["name"]
		self.type = definition["type"]
		self.chartJSON = definition["chartJSON"]

	def JSONChart(self):
		return self.chartJSON


# Default function is main()
if __name__ == '__main__':
    main()