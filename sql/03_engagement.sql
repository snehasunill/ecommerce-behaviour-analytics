-- Landmark design: exactly 7 days of exposure, then a disjoint 30-day purchase outcome.
-- Do NOT use engagement measured after outcome starts or purchases during exposure as outcome.
-- Includes only visitors with full 37-day follow-up to dataset end.
CREATE OR REPLACE TABLE engagement_visitors AS
WITH boundaries AS (SELECT MAX(event_ts) AS last_ts FROM events),
first_seen AS (SELECT visitorid, MIN(event_ts) AS first_ts FROM events GROUP BY visitorid),
eligible AS (
 SELECT f.visitorid, f.first_ts FROM first_seen f CROSS JOIN boundaries b
 WHERE f.first_ts + INTERVAL 37 DAY <= b.last_ts
), pre AS (
 SELECT e.visitorid, COUNT(*) AS first_week_events,
        COUNT(DISTINCT CAST(e.event_ts AS DATE)) AS first_week_active_days,
        COUNT(DISTINCT e.itemid) AS first_week_items,
        SUM(CASE WHEN e.event='addtocart' THEN 1 ELSE 0 END) AS first_week_carts
 FROM eligible a JOIN events e ON a.visitorid=e.visitorid
 AND e.event_ts>=a.first_ts AND e.event_ts<a.first_ts+INTERVAL 7 DAY
 GROUP BY e.visitorid
), outcome AS (
 SELECT a.visitorid, MAX(CASE WHEN e.event='transaction' THEN 1 ELSE 0 END) AS purchase_next_30d
 FROM eligible a LEFT JOIN events e ON a.visitorid=e.visitorid
 AND e.event_ts>=a.first_ts+INTERVAL 7 DAY AND e.event_ts<a.first_ts+INTERVAL 37 DAY
 GROUP BY a.visitorid
)
SELECT a.visitorid, a.first_ts, p.first_week_events, p.first_week_active_days,
       p.first_week_items, p.first_week_carts, o.purchase_next_30d,
       CASE WHEN p.first_week_active_days>=2 THEN '2+ active days' ELSE '1 active day' END engagement_group
FROM eligible a JOIN pre p USING(visitorid) JOIN outcome o USING(visitorid);

CREATE OR REPLACE TABLE engagement_summary AS
SELECT engagement_group, COUNT(*) visitors, SUM(purchase_next_30d) buyers,
ROUND(100.0*SUM(purchase_next_30d)/NULLIF(COUNT(*),0),3) AS purchase_pct,
AVG(first_week_events) AS avg_first_week_events
FROM engagement_visitors GROUP BY engagement_group;

CREATE OR REPLACE TABLE daily_activity AS
SELECT CAST(event_ts AS DATE) AS event_date, event, COUNT(*) AS event_count,
       COUNT(DISTINCT visitorid) AS unique_visitors
FROM events GROUP BY 1,2;
