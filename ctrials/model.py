#!/usr/bin/python
#from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

###
# Model classes
###

Base = declarative_base()

class CTrialsModelMixin(object):
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


class InterventionType(Base, CTrialsModelMixin):
	__tablename__ = 'interventionTypes'

	itype = Column('type', String, unique=True)

	def __init__(self, itype):
		self.itype = itype


class Intervention(Base, CTrialsModelMixin):
	__tablename__ = 'interventions'

	trial_id = Column(Integer, ForeignKey("trials.id", ondelete='cascade'))
	type_id = Column(Integer, ForeignKey("interventionTypes.id"))
	name = Column(String)

	itype = relationship("InterventionType")

	def __init__(self, name, itype):
		self.name = name
		self.itype = itype


class SponsorClass(Base, CTrialsModelMixin):
	__tablename__ = 'sponsorClasses'

	sclass = Column('class', String, unique=True)

	def __init__(self, sclass):
		self.sclass = sclass


class Sponsor(Base, CTrialsModelMixin):
	__tablename__ = 'sponsors'

	sclass_id = Column('class_id', Integer, ForeignKey("sponsorClasses.id"))
	name = Column(String, unique=True)
	shortName = Column(String)

	sclass = relationship("SponsorClass")

	def __init__(self, name, shortName, sclass):
		self.name = name
		self.shortName = shortName
		self.sclass = sclass


trial_countries = Table('trialCountries', Base.metadata,
	Column('trial_id', Integer, ForeignKey("trials.id")),
	Column('country_id', Integer, ForeignKey("countries.id"))
	)


class Trial(Base, CTrialsModelMixin):
	__tablename__ = 'trials'

	nctID = Column(String, unique=True, nullable=False)
	title = Column(String)
	status = Column(String)
	startDate = Column(Date)
	completionDate = Column(Date)
	primaryCompletionDate = Column(Date)
	resultsDate = Column(Date)
	lastChangedDate = Column(Date)
	phaseMask = Column(Integer)
	includedInPrayle = Column(Boolean)

	# Non-Foreign Key properties. Used for populating the object from an XMLTrial
	domesticKeys = ['nctID', 'title', 'status', 'startDate', 'completionDate', 'includedInPrayle',
					'primaryCompletionDate', 'resultsDate', 'phaseMask', 'lastChangedDate']

	# Foreign Keys
	countries = relationship('Country', secondary=trial_countries, backref='trials')

	sponsor_id = Column(Integer, ForeignKey("sponsors.id"))
	sponsor = relationship('Sponsor', backref='trials')

	interventions = relationship('Intervention', cascade="all, delete, delete-orphan", single_parent=True)

	def __init__(self, nctID):
		self.nctID = nctID



class Country(Base, CTrialsModelMixin):
	__tablename__ = 'countries'

	name = Column(String, unique=True, nullable=False)

	def __init__(self, name):
		self.name = name



# http://stackoverflow.com/a/9264556/1749551
def deleteSponsorOrphans(session, ctx):
	print "after_flush has run"
	session.query(Sponsor).\
		filter(~Sponsor.trials.any()).\
		delete(synchronize_session=False)