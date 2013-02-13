#!/usr/bin/python

import os, os.path, subprocess

def main():
	firstLine = True
	for root, _, files in os.walk("study_fields_xml"):
		for f in files:
			fullpath = os.path.join(root, f)
			
			if firstLine:
				print "\n".join(runXSLT(fullpath)[1:2])
				firstLine = False
			else:
				print runXSLT(fullpath)[2]

def runXSLT(path):
	p = subprocess.check_output(["xsltproc", "process_xml.xslt", path])
	return p.split("\n")

# Default function is main()
if __name__ == '__main__':
	main()

