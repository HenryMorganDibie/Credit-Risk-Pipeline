-- SQL Query for Executive Credit Portfolio Monitoring Dashboard

-- Objective: Calculate key risk and exposure metrics broken down by the 
-- Machine Learning-driven Risk Segment.
SELECT
    risk_segment,
    COUNT(customer_id) AS total_customers_approved,
    SUM(CASE WHEN loan_status = 'Default' THEN 1 ELSE 0 END) AS total_defaults,
    
    -- Key KPI 1: Portfolio Default Rate (PDR) by Segment
    (SUM(CASE WHEN loan_status = 'Default' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id)) AS portfolio_default_rate_pct,
    
    -- Key KPI 2: Total Exposure (Outstanding Balance)
    SUM(outstanding_balance) AS total_outstanding_exposure,
    
    -- Key KPI 3: Average Expected Profitability
    AVG(expected_profit_loss) AS avg_expected_pnl_per_customer
FROM
    CreditPortfolioMonitor
GROUP BY 1
ORDER BY portfolio_default_rate_pct DESC;