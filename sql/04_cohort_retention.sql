-- First-observed cohorts (not signups). Retention is activity on EXACT calendar day N.
-- Visitors too close to observation end are excluded from each horizon's denominator.
CREATE OR REPLACE TABLE cohort_retention AS
WITH seen AS (
 SELECT visitorid, MIN(CAST(event_ts AS DATE)) AS cohort_date
 FROM events GROUP BY visitorid
), active AS (
 SELECT DISTINCT visitorid, CAST(event_ts AS DATE) AS active_date FROM events
), max_date AS (SELECT MAX(CAST(event_ts AS DATE)) AS final_date FROM events),
horizons AS (SELECT 1 AS day_n UNION ALL SELECT 7 UNION ALL SELECT 30),
valid AS (
 SELECT s.visitorid, s.cohort_date, h.day_n
 FROM seen s CROSS JOIN horizons h CROSS JOIN max_date m
 WHERE s.cohort_date + h.day_n <= m.final_date
)
SELECT DATE_TRUNC('week',v.cohort_date)::DATE AS cohort_week, v.day_n,
       COUNT(*) AS eligible_visitors, COUNT(a.visitorid) AS returned_visitors,
       ROUND(100.0*COUNT(a.visitorid)/NULLIF(COUNT(*),0),3) AS return_pct
FROM valid v LEFT JOIN active a
 ON a.visitorid=v.visitorid AND a.active_date=v.cohort_date+v.day_n
GROUP BY 1,2 ORDER BY 1,2;
