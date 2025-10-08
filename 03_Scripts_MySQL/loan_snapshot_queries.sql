USE LoanDataAnalysis;

-- ====================================================================
-- 1. Aggregation: Total Cumulative Repayment and Interest at Final Day
-- ====================================================================
-- This query returns the final repayment and interest figures for each customer.
SELECT
    customer_id,
    cumulative_repayment,
    cumulative_interest
FROM
    LoanSnapshot
WHERE
    -- Select the row with the maximum date for each customer (the final day)
    (customer_id, `date`) IN (
        SELECT customer_id, MAX(`date`)
        FROM LoanSnapshot
        GROUP BY customer_id
    )
ORDER BY
    customer_id;


-- ====================================================================
-- 2. Utilization Analysis: Average Utilization on the Final Day
-- ====================================================================
SELECT
    AVG(utilization_pct) AS average_final_utilization
FROM
    LoanSnapshot
WHERE
    -- Select the row with the maximum date for each customer (the final day)
    (customer_id, `date`) IN (
        SELECT customer_id, MAX(`date`)
        FROM LoanSnapshot
        GROUP BY customer_id
    );


-- ====================================================================
-- 3. Arrears Tracking: Maximum Days in Arrears Observed
-- ====================================================================
-- This helps identify customers who hit the highest level of delinquency.
SELECT
    customer_id,
    MAX(days_in_arrears) AS max_days_in_arrears
FROM
    LoanSnapshot
GROUP BY
    customer_id
ORDER BY
    max_days_in_arrears DESC;


-- ====================================================================
-- 4. Risk Segmentation: Count Customers in Each Risk Band at Final Day
-- ====================================================================
SELECT
    risk_band,
    COUNT(customer_id) AS num_customers
FROM
    LoanSnapshot
WHERE
    -- Select the row with the maximum date for each customer
    (customer_id, `date`) IN (
        SELECT customer_id, MAX(`date`)
        FROM LoanSnapshot
        GROUP BY customer_id
    )
GROUP BY
    risk_band
ORDER BY
    num_customers DESC;


-- ====================================================================
-- 5. Cohort Question: Count of Fully Paid Off Loans (Outstanding Balance = 0)
-- ====================================================================
SELECT
    COUNT(T1.customer_id) AS fully_paid_off_customers
FROM
    LoanSnapshot AS T1
WHERE
    T1.outstanding_balance = 0
    -- Ensure we are only counting based on the latest record for each customer
    AND (T1.customer_id, T1.`date`) IN (
        SELECT customer_id, MAX(`date`)
        FROM LoanSnapshot
        GROUP BY customer_id
    );


-- ====================================================================
-- 6. Trend Question: Day-by-Day Change in Cumulative Paid (e.g., Daily Repayment)
-- ====================================================================
-- Shows daily repayment activity for a specific customer ('C001' is an example)
SELECT
    `date`,
    cumulative_paid,
    -- Calculate the difference from the previous day's cumulative paid amount
    cumulative_paid - LAG(cumulative_paid, 1, 0) OVER (
        PARTITION BY customer_id
        ORDER BY `date`
    ) AS daily_repayment_amount
FROM
    LoanSnapshot
WHERE
    customer_id = 'C001' -- CHANGE THIS ID to analyze a different customer
ORDER BY
    `date`;


-- ====================================================================
-- 7. Advanced Metric: Average Recovery Rate for Defaulters
-- ====================================================================

-- This metric shows how much money (as a % of the original loan) we recover 
-- on average from customers who hit a high delinquency level (Defaulted).
-- Definition: A customer is a 'Defaulter' if max_days_in_arrears > 5.

WITH MaxArrears AS (
    -- Step 1: Find the maximum arrears observed for each customer
    SELECT
        customer_id,
        MAX(days_in_arrears) AS max_arrears
    FROM
        LoanSnapshot
    GROUP BY
        customer_id
),
FinalSnapshot AS (
    -- Step 2: Get the final status (cumulative_repayment and loan_amount) for all customers
    -- We assume 'loan_amount' is available on the final snapshot row.
    SELECT
        customer_id,
        cumulative_repayment,
        loan_amount 
    FROM
        LoanSnapshot
    WHERE
        -- Filter to ensure we only get the latest row for each customer
        (customer_id, `date`) IN (
            SELECT customer_id, MAX(`date`)
            FROM LoanSnapshot
            GROUP BY customer_id
        )
)
-- Step 3: Join the two results and calculate the final Recovery Rate
SELECT
    -- Calculate the average (Cumulative Repayment / Loan Amount) ratio for defaulters
    AVG(T2.cumulative_repayment / T2.loan_amount) AS average_recovery_rate_defaulters
FROM
    MaxArrears AS T1
JOIN
    FinalSnapshot AS T2 ON T1.customer_id = T2.customer_id
WHERE
    T1.max_arrears > 5; -- Filter for Defaulters (max arrears > 5 days)    