#!/usr/bin/python

import os.path

def relativePath(path):
	"""Returns a path made relative to this file's directory"""
	module_dir, module_file = os.path.split(__file__)
	return os.path.join(module_dir, path)
