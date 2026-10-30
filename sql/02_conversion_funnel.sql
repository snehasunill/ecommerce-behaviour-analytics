-- Ordered VISITOR funnel, not event counts or continuous sessions.
-- Tie-break: a step must occur at a strictly later millisecond than its predecessor.
-- Same visitor may interact with different items; purchase need not correspond to carted item.
CREATE OR REPLACE TABLE funnel_visitors AS
WITH first_views AS (
    SELECT visitorid, MIN(timestamp_ms) AS view_ms
    FROM events WHERE event='view' GROUP BY visitorid
), first_carts AS (
    SELECT v.visitorid, MIN(e.timestamp_ms) AS cart_ms
    FROM first_views v JOIN events e ON v.visitorid=e.visitorid
      AND e.event='addtocart' AND e.timestamp_ms>v.view_ms
    GROUP BY v.visitorid
), first_purchases AS (
    SELECT c.visitorid, MIN(e.timestamp_ms) AS purchase_ms
    FROM first_carts c JOIN events e ON c.visitorid=e.visitorid
      AND e.event='transaction' AND e.timestamp_ms>c.cart_ms
    GROUP BY c.visitorid
)
SELECT v.visitorid, v.view_ms, c.cart_ms, p.purchase_ms
FROM first_views v LEFT JOIN first_carts c USING(visitorid)
LEFT JOIN first_purchases p USING(visitorid);

CREATE OR REPLACE TABLE funnel_summary AS
WITH totals AS (
  SELECT COUNT(*) AS viewed, COUNT(cart_ms) AS carted, COUNT(purchase_ms) AS purchased
  FROM funnel_visitors
)
SELECT viewed, carted, purchased,
       ROUND(100.0*carted/NULLIF(viewed,0),2) AS view_to_cart_pct,
       ROUND(100.0*purchased/NULLIF(carted,0),2) AS cart_to_purchase_pct,
       ROUND(100.0*purchased/NULLIF(viewed,0),2) AS view_to_purchase_pct,
       ROUND(100.0*(carted-purchased)/NULLIF(carted,0),2) AS cart_dropoff_pct
FROM totals;
