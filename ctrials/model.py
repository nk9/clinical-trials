#!/usr/bin/python
#from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

###
# Model classes
###

Base = declarative_base()

class MyMixin(object):
	# @declared_attr
	# def __tablename__(cls):
	# 	return cls.__name__.lower()

	id = Column(Integer, primary_key=True)

	def __repr__(self):
		print self.__dict__
		valuesString = ""
		for k, v in self.__dict__.items():
			if k == '_sa_instance_state':
				continue

			if len(valuesString):
				valuesString += ", "
				
			valuesString += '"%s"' % v

		return "<%s(%s)>" % (type(self), valuesString)


class Trial(Base, MyMixin):
	__tablename__ = 'trials'

	nctID = Column(String)
	title = Column(String)

	def __init__(self, nctID, title):
		self.nctID = nctID
		self.title = title

	# def __repr__(self):
	# 	return "<Trial('%s', '%s')>" % (self.nctID, self.title)


class Country(Base, MyMixin):
	__tablename__ = 'countries'

	name = Column(String)

	def __init__(self, name):
		self.name = name


# class InterventionType(Base, MyMixin):
# 	__tablename__ = 'interventionTypes'

# 	type = Column(String)

# 	def