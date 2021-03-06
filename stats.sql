# Count of no-results trials
SELECT COUNT(class)
FROM trials, sponsors, sponsorClasses
WHERE trials.sponsor_id = sponsors.id
AND sponsors.class_id = sponsorClasses.id
AND resultsDate IS NULL;


# Counts of no-results trials by sponsor class
# id=missing_by_sector
SELECT class, COUNT(class)
FROM trials AS t, sponsors, sponsorClasses
WHERE t.sponsor_id = sponsors.id
AND sponsors.class_id = sponsorClasses.id
AND resultsDate IS NULL
AND t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY class;


# Counts of no-results trials by intervention type
SELECT allTrials.type, allTrials.count, haveResults.count
FROM
(SELECT type, COUNT(type) as count
FROM trials, interventions, interventionTypes
WHERE trials.id = interventions.trial_id
AND interventionTypes.id = interventions.type_id
AND trials.resultsDate IS NULL
AND trials.completionDate IS NOT NULL
GROUP BY type) as allTrials
LEFT JOIN
(SELECT type, COUNT(type) as count
FROM trials, interventions, interventionTypes
WHERE trials.id = interventions.trial_id
AND interventionTypes.id = interventions.type_id
AND trials.resultsDate IS NOT NULL
AND trials.completionDate IS NOT NULL
GROUP BY type) as haveResults
ON allTrials.type = haveResults.type
GROUP BY allTrials.type;


# List of all completed trials vs. those which have results by year completed
# id=completed_vs_reported
SELECT allTrials.year, allTrials.count-haveResults.count, haveResults.count
FROM
(SELECT strftime('%Y',t.completionDate) AS year, COUNT(t.id) AS count
FROM trials AS t
WHERE t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY year) AS allTrials
LEFT JOIN
(SELECT strftime('%Y', t.completionDate) AS year, COUNT(t.id) as count
FROM trials AS t
WHERE t.resultsDate > 0 AND t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY year) AS haveResults
ON allTrials.year = haveResults.year
GROUP BY allTrials.year;


# List of sponsors with most outstanding results
# id=10_most_unreporting_sponsors
SELECT noResults.sponsorName, haveResults.count, noResults.count
FROM
(SELECT s.id AS sponsor, ifnull(s.shortName, s.name) as sponsorName, COUNT(t.id) AS count
FROM trials AS t, sponsors AS s
WHERE s.id = t.sponsor_id
AND t.resultsDate IS NULL
AND t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY sponsor_id
ORDER BY count DESC) AS noResults
LEFT JOIN
(SELECT s.id AS sponsor, COUNT(t.id) AS count
FROM trials as t, sponsors AS s
WHERE s.id = t.sponsor_id
AND t.resultsDate IS NOT NULL
AND t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY sponsor_id
ORDER BY count DESC) AS haveResults
ON noResults.sponsor = haveResults.sponsor
LIMIT 10;


# Missing results by study phase
# id=missing_by_phase
SELECT IFNULL(t.phaseMask, 0), COUNT(t.id) as count
FROM trials as t
WHERE t.resultsDate IS NULL
AND t.completionDate BETWEEN date('2000-01-01') AND date('now', '-1 year')
GROUP BY t.phaseMask
ORDER BY t.phaseMask;


# Prayle studies breakdown, by sponsor class
# id=prayle_then_and_now
SELECT a.class, a.count, b.count, c.count
FROM
(SELECT COUNT(t.id) AS count, sc.class AS class
FROM trials AS t, sponsors AS s, sponsorClasses AS sc
WHERE s.id = t.sponsor_id
AND s.class_id = sc.id
AND t.includedInPrayle = 1
AND t.resultsDate BETWEEN date('2009-01-01') AND date('2011-01-18')
GROUP BY sc.id) AS a
LEFT JOIN
(SELECT COUNT(t.id) AS count, sc.class AS class
FROM trials AS t, sponsors AS s, sponsorClasses AS sc
WHERE s.id = t.sponsor_id
AND s.class_id = sc.id
AND t.includedInPrayle = 1
AND t.resultsDate BETWEEN date('2011-01-18') AND date('now')
GROUP BY sc.id) AS b
ON a.class = b.class
LEFT JOIN
(SELECT COUNT(t.id) AS count, sc.class AS class
FROM trials AS t, sponsors AS s, sponsorClasses AS sc
WHERE s.id = t.sponsor_id
AND s.class_id = sc.id
AND t.includedInPrayle = 1
AND t.resultsDate = 0
GROUP BY sc.id) AS c
ON a.class = c.class;