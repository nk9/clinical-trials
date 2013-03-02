#!/usr/bin/python

import json
import os

def create(chartsPath):
	createCharts(chartsPath, loadChartDefs())


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

def createCharts(chartsPath, chartDefs):
	for chartDef in chartDefs:
		chart = Chart(chartDef)
		chart.output(chartsPath)


class Chart(object):
	def __init__(self, definition):
		self.sql = definition["sql"]
		self.name = definition["name"]
		self.templateFile = definition["templateFile"]

		self.loadTemplate()

	def loadTemplate(self):
		module_dir, module_file = os.path.split(__file__)
		print open(os.path.join(module_dir, 'templates', self.templateFile)).read()

	def output(self, chartsPath):
		print "=== Write to %s" % (os.path.join(chartsPath, self.templateFile))


# Default function is main()
if __name__ == '__main__':
    main()