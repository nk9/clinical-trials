CREATE TABLE countries (
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE
);

CREATE TABLE sponsorClasses (
	id INTEGER PRIMARY KEY,
	class TEXT UNIQUE
);

CREATE TABLE sponsors (
	id INTEGER PRIMARY KEY,
	name TEXT UNIQUE,
	class_id INTEGER,
	FOREIGN KEY (class_id) REFERENCES sponsorClasses(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE trials (
	id INTEGER PRIMARY KEY,
	sponsor_id INTEGER,
	title TEXT,
	nctID TEXT UNIQUE NOT NULL,
	status TEXT,
	startDate INTEGER,
	completionDate INTEGER,
	primaryCompletionDate INTEGER,
	resultsDate INTEGER,
	phaseMask INTEGER,
	includedInPrayle INTEGER,
	FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE interventions (
	id INTEGER PRIMARY KEY,
	trial_id INTEGER,
	type_id INTEGER,
	name TEXT,
	FOREIGN KEY (type_id) REFERENCES interventionTypes(id),
	FOREIGN KEY (trial_id) REFERENCES trials(id)
);

CREATE TABLE interventionTypes (
	id INTEGER PRIMARY KEY,
	type TEXT UNIQUE
);

CREATE TABLE trialCountries (
	trial_id INTEGER,
	country_id INTEGER,
	FOREIGN KEY(trial_id) REFERENCES trials(id) ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY(country_id) REFERENCES countries(id) ON DELETE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY (trial_id, country_id)
);
