-- ============================================================
-- Sales Intelligence & Forecasting Platform
-- SQL Business Analysis
-- Database: sales_warehouse
-- ============================================================

USE sales_warehouse;


-- ============================================================
-- 1. Executive Summary KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT Invoice_No) AS total_invoices,
    COUNT(DISTINCT Customer_Id) AS total_customers,
    SUM(Revenue) AS total_revenue
FROM sales_transactions;

-- ============================================================
-- 2. Monthly Revenue Trend
-- ============================================================

SELECT
    Year,
    Month,
    SUM(Revenue) AS total_revenue
FROM sales_transactions
GROUP BY Year, Month
ORDER BY Year, Month;

-- ============================================================
-- 3. Revenue by Country
-- ============================================================

SELECT
    Country,
    SUM(Revenue) AS total_revenue
FROM sales_transactions
GROUP BY Country
ORDER BY total_revenue DESC;

-- ============================================================
-- 4. Top 10 Customers by Revenue
-- ============================================================

SELECT
    Customer_Id,
    COUNT(DISTINCT Invoice_No) AS total_orders,
    SUM(Revenue) AS total_revenue
FROM sales_transactions
GROUP BY Customer_Id
ORDER BY total_revenue DESC
LIMIT 10;

-- ============================================================
-- 5. Top 10 Products by Revenue
-- ============================================================

SELECT
    Stock_Code,
    MAX(Description) AS Product,
    SUM(Quantity) AS total_quantity,
    SUM(Revenue) AS total_revenue
FROM sales_transactions
GROUP BY Stock_Code
ORDER BY total_revenue DESC
LIMIT 10;

-- ============================================================
-- 6. Average Order Value
-- ============================================================

SELECT
    SUM(Revenue) / COUNT(DISTINCT Invoice_No) AS average_order_value
FROM sales_transactions;

-- ============================================================
-- 7. First and last transaction
-- ============================================================

SELECT
    MIN(Invoice_Date) AS first_transaction,
    MAX(Invoice_Date) AS last_transaction
FROM sales_transactions;