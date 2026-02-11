--Query 1:  Total Row Count
SELECT COUNT(*) as clean_row_count 
FROM "retail-db"."clean-processed";

--Query 2: Should return 0 if your ETL job worked correctly
SELECT COUNT(*) as bad_rows
FROM "retail-db"."clean-processed"
WHERE customerid IS NULL;

--Query 3: Partition Verification
SELECT DISTINCT country 
FROM "retail-db"."clean-processed"
ORDER BY country;