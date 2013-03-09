clinical-trials
===============

This is a Python module and some scripts for importing ClinicalTrials.gov data to an SQLite3 database and then generating pretty charts with that data. It consumes XML files downloaded from ClinicalTrials.gov. More information about this can be found here:

http://clinicaltrials.gov/ct2/resources/download

Any requirements?
-----------------

These scripts were developed using Mac OS X 10.8, which ships with Python v2.7.2. No testing has been done on other versions of Python, although you are welcome to submit patches. It also uses Highcharts v2.3.5, a very straightforward and powerful JS graphing library. It is free for non-commercial use. See here for more information:

http://shop.highsoft.com/highcharts.html

How do I use it?
----------------
```bash
$ python trials.py --createDB --xmlFilesPath trials_xml/ trialsDB.sqlite3
# This will take a good few minutes if you have the full database

$ python trials.py trialsDB.sqlite3
$ open web/charts.html
```
