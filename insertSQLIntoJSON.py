#!/usr/bin/python

import json
import sys

def main():
	chartsFileName = "ctrials/charts.json"
	statsFileName = "stats.sql"

	chartsJSONFile = open(chartsFileName)
	try:
		jsonDict = json.load(chartsJSONFile)
	except Exception:
		print "Failed reading file: " + chartsFileName + " Check your JSON!"
		sys.exit()

	chartsJSONFile.close()

	sqlFile = open(statsFileName)
	queries = {}
	currentID = ""
	appendLine = False

	for line in sqlFile.readlines():
		# print "==" + line.replace("\n", '\\n') + "=="
		if appendLine:
			if line == "\n": # empty line
				# print queries[currentID]
				appendLine = False
			elif len(line) == 0: # EOF reached
				appendLine = False
			else:
				# print "(appending)"
				queries[currentID].append(line.strip())

		if line.startswith("# id="):
			appendLine = True
			currentID = line[5:].strip()
			queries[currentID] = []

	sqlFile.close()

	for (id, sql) in queries.iteritems():
		if id in jsonDict:
			jsonDict[id]['sql'] = sql
			print "Added '" + id + "'"
		else:
			print "'%s' missing from %s" % (id, chartsFileName)


	chartsJSONFile = open(chartsFileName, "w")
	jsonString = json.dump(jsonDict, chartsJSONFile, sort_keys=True, indent=4, separators=(',', ' : '))
	chartsJSONFile.close()


# Default function is main()
if __name__ == '__main__':
    main()