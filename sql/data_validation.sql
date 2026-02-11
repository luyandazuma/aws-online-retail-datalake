--Query 1: Check for records with invalid negative values
SELECT COUNT(*) as invalid_records
FROM "retail-db"."clean-processed"
WHERE quantity < 0 OR unitprice < 0;

--Query 2: Check for orders with future dates (impossible)
SELECT COUNT(*) as future_orders
FROM "retail_db"."clean_processed"
WHERE invoicedate > current_date;

--Query 3: Check for transactions with unknown countries
SELECT COUNT(*) as unknown_country_count
FROM "retail_db"."clean_processed"
WHERE country IS NULL OR country = '';