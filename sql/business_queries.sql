--Query 1: Top 10 Revenue Generating Countries
SELECT 
    country, 
    SUM(totalamount) as total_revenue
FROM "retail-db"."clean-processed"
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;

--Query 2: Best Selling Products by Quantity
SELECT 
    description, 
    SUM(quantity) as total_sold
FROM "retail-db"."clean-processed"
GROUP BY description
ORDER BY total_sold DESC
LIMIT 10;

--Query 3: Cost Optimization
-- This query scans very little data because of partitioning
SELECT * FROM "retail-db"."clean-processed"
WHERE country = 'France' 
LIMIT 10;

--Query 4: Monthly Revenue Trend (Time-Series)
SELECT 
    date_trunc('month', invoicedate) as sales_month, 
    SUM(totalamount) as monthly_revenue,
    COUNT(DISTINCT invoiceno) as total_orders
FROM "retail-db"."clean-processed"
GROUP BY 1
ORDER BY 1;

--Query 5: Customer Lifetime Value
SELECT 
    customerid, 
    SUM(totalamount) as lifetime_spend,
    COUNT(DISTINCT invoiceno) as total_orders,
    AVG(totalamount) as avg_spend_per_order
FROM "retail-db"."clean-processed"
GROUP BY customerid
ORDER BY lifetime_spend DESC
LIMIT 10;

--Query 6: Order Value Average by Country
SELECT 
    country,
    COUNT(DISTINCT invoiceno) as total_orders,
    SUM(totalamount) as total_revenue,
    (SUM(totalamount) / COUNT(DISTINCT invoiceno)) as avg_order_value
FROM "retail-db"."clean-processed"
GROUP BY country
HAVING COUNT(DISTINCT invoiceno) > 10  
ORDER BY avg_order_value DESC;