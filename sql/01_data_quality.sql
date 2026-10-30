-- Event type and transaction ID consistency; repeated actions are not automatically duplicate ingestion.
SELECT event, COUNT(*) AS event_rows, COUNT(DISTINCT visitorid) AS visitors,
       SUM(CASE WHEN visitorid IS NULL OR itemid IS NULL THEN 1 ELSE 0 END) AS null_keys,
       SUM(CASE WHEN event_ts IS NULL THEN 1 ELSE 0 END) AS bad_timestamps,
       SUM(CASE WHEN event = 'transaction' AND transactionid IS NULL THEN 1 ELSE 0 END) AS missing_transaction_ids,
       SUM(CASE WHEN event <> 'transaction' AND transactionid IS NOT NULL THEN 1 ELSE 0 END) AS unexpected_transaction_ids
FROM events GROUP BY event ORDER BY event;
