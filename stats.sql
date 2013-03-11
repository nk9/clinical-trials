# Count of no-results trials
SELECT COUNT(class)
FROM trials, sponsors, sponsorClasses
WHERE trials.sponsor_id = sponsors.id
AND sponsors.class_id = sponsorClasses.id
AND resultsDate = 0;


# Counts of no-results trials by sponsor class
# id=missing_by_sector
SELECT class, COUNT(class)
FROM trials, sponsors, sponsorClasses
WHERE trials.sponsor_id = sponsors.id
AND sponsors.class_id = sponsorClasses.id
AND resultsDate = 0
GROUP BY class;


# Counts of no-results trials by intervention type
SELECT allTrials.type, allTrials.count, haveResults.count
FROM
(SELECT type, COUNT(type) as count
FROM trials, interventions, interventionTypes
WHERE trials.id = interventions.trial_id
AND interventionTypes.id = interventions.type_id
AND trials.resultsDate = 0
AND trials.completionDate > 0
GROUP BY type) as allTrials
LEFT JOIN
(SELECT type, COUNT(type) as count
FROM trials, interventions, interventionTypes
WHERE trials.id = interventions.trial_id
AND interventionTypes.id = interventions.type_id
AND trials.resultsDate > 0
AND trials.completionDate > 0
GROUP BY type) as haveResults
ON allTrials.type = haveResults.type
GROUP BY allTrials.type;


# List of all completed trials vs. those which have results by year commenced
# id=completed_vs_reported
SELECT allTrials.year, allTrials.count-haveResults.count, haveResults.count
FROM
(SELECT strftime('%Y',t.completionDate) AS year, COUNT(t.id) AS count
FROM trials AS t
WHERE t.completionDate BETWEEN date('2000-01-01') AND date('now')
GROUP BY year) AS allTrials
LEFT JOIN
(SELECT strftime('%Y', t.completionDate) AS year, COUNT(t.id) as count
FROM trials AS t
WHERE t.resultsDate > 0 AND t.completionDate BETWEEN date('2000-01-01') AND date('now')
GROUP BY year) AS haveResults
ON allTrials.year = haveResults.year
GROUP BY allTrials.year;


# List of sponsors with most outstanding results
# id=10_most_unreporting_sponsors
SELECT ifnull(s.shortName, s.name), COUNT(t.id) as count
FROM trials AS t, sponsors AS s
WHERE s.id = t.sponsor_id
AND t.resultsDate = 0
AND t.completionDate BETWEEN date('2000-01-01') AND date('now')
GROUP BY sponsor_id
ORDER BY count DESC
LIMIT 10;