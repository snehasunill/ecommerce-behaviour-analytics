-- Descriptive item event ratios (not unique-user conversion or causal estimates).
-- A minimum of 100 views prevents low-support rankings.
CREATE OR REPLACE TABLE item_metrics AS
WITH item_counts AS (
 SELECT itemid,
   COUNT(*) FILTER(WHERE event='view') AS views,
   COUNT(*) FILTER(WHERE event='addtocart') AS carts,
   COUNT(*) FILTER(WHERE event='transaction') AS purchases,
   COUNT(DISTINCT visitorid) AS observed_visitors
 FROM events WHERE itemid IS NOT NULL GROUP BY itemid
 HAVING COUNT(*) FILTER(WHERE event='view') >= 100
)
SELECT *, ROUND(100.0*carts/NULLIF(views,0),2) AS cart_events_per_100_views,
ROUND(100.0*purchases/NULLIF(views,0),2) AS purchase_events_per_100_views
FROM item_counts;
