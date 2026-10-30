-- OPTIONAL, potentially expensive: resolve category as of each event timestamp.
-- Restrict to high-support items to avoid exploding historical property joins.
-- At a property timestamp, conflicting category rows are explicitly ambiguous.
CREATE OR REPLACE TABLE item_categories_pit AS
WITH supported AS (SELECT itemid FROM item_metrics),
category_updates AS (
 SELECT p.itemid, p.timestamp_ms,
        CASE WHEN COUNT(DISTINCT p.value)=1 THEN TRY_CAST(MIN(p.value) AS BIGINT)
             ELSE NULL END AS categoryid,
        CASE WHEN COUNT(DISTINCT p.value)=1 THEN 'mapped' ELSE 'ambiguous' END AS mapping_status
 FROM item_properties p INNER JOIN supported s USING(itemid)
 WHERE p.property='categoryid'
 GROUP BY p.itemid,p.timestamp_ms
), intervals AS (
 SELECT itemid, timestamp_ms AS starts_ms,
        LEAD(timestamp_ms) OVER(PARTITION BY itemid ORDER BY timestamp_ms) AS ends_ms,
        categoryid,mapping_status
 FROM category_updates
)
SELECT e.itemid,e.timestamp_ms,e.event,e.visitorid,
       i.categoryid,COALESCE(i.mapping_status,'unmapped') AS mapping_status
FROM events e JOIN supported s ON e.itemid=s.itemid
LEFT JOIN intervals i ON e.itemid=i.itemid AND e.timestamp_ms>=i.starts_ms
 AND (e.timestamp_ms<i.ends_ms OR i.ends_ms IS NULL);
