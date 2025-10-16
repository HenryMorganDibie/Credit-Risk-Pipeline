# Digital Bank Loan Analysis Project (Data Engineering & Portfolio Risk Strategy)

## Project Overview

This project simulates a data engineering and financial analysis pipeline designed to load, organize, and analyze a loan snapshot dataset. The goal is to calculate key portfolio risk metrics and provide analytical interpretations of customer repayment behavior. This project showcases advanced proficiency in **Python data handling, secure credential management, advanced SQL querying, Credit Risk Modeling, and end-to-end workflow automation**.

The pipeline covers the entire customer lifecycle, translating model outputs into actionable financial KPIs for leadership. It demonstrates core skills in:

- **Workflow Automation/MLOps:** Orchestrating 7 complex, multi-step jobs via a single PowerShell script.
- **Credit Risk Strategy:** P&L maximization and data-driven credit limit assignment.
- **Data Engineering:** Secure ETL, feature generation using advanced SQL, and system integration.
- **Executive Reporting:** Translating model outputs into actionable financial KPIs for leadership.

---

## Key Technologies Used

| Technology | Purpose |
|------------|---------|
| Python/Pandas/Scikit-learn | Data manipulation, Logistic Regression, K-Means Clustering |
| SQLAlchemy/MySQL | Database connection, ingestion, and complex feature extraction |
| PowerShell (`run_pipeline.ps1`) | Master script for sequential pipeline automation |
| Matplotlib/Seaborn | Data visualization and executive dashboarding |

---

## Project Structure & Automation

The project is structured to maximize reproducibility and clarity, mirroring a production environment. The entire workflow is executed via a single PowerShell script (`run_pipeline.ps1`).

| Folder | Key Files & Purpose |
|--------|-------------------|
| 01_Data_Input/ | Contains the source Excel data (`Loan_Snapshot_Interview_Dataset.xlsx`) |
| 02_Scripts_Python/ | Core logic: Model_Training_V1_Base.py (Base model), Model_Training_V2_Scoring.py (Scoring model), `data_loader_excel_to_mysql.py`, `Model_Training_V2_Scoring.py`, `Cutoff_Optimization.py`, `Credit_Limit_Clustering.py`, `ETL_Portfolio_Setup.py` |
| 03_Scripts_MySQL/ | Feature engineering (`loan_snapshot_queries.sql`) and monitoring logic (`loan_monitoring_queries.sql`) |
| 04_Analysis_Outputs/ | 17 final analytical results (KPIs, plots, and outputs like `Credit_Limit_Recommendations.csv` and `04_KMeans_Elbow_Plot.png`) |
| 05_Visualizations_Python/ | Reporting: `Viz_Historical_Analysis.py` (Foundational Plots) and `Viz_Dashboard_KPIs.py` (Executive Dashboard) |

---

## Pipeline Automation & Execution Flow

| Phase | Description | Key Script / Output(s) |
|-------|------------|------------------------|
| 0.1 ETL & SQL Analysis | Reads raw data, cleans it, and loads into MySQL; executes 7 core SQL feature-generation queries | `data_loader_excel_to_mysql.py` (Data loaded to `loansnapshot` table) |
| 0.2 Foundational Visuals | Generates initial historical charts for risk distribution and repayment trends | `Viz_Historical_Analysis.py` / `01_Max_Arrears_Histogram.png`, `02_Portfolio_Repayment_Trend.png` |
| 1.1 Credit Scoring | Trains Logistic Regression model and generates scores for the entire portfolio | `Model_Training_V2_Scoring.py` / `Model_Scoring_Output.csv` |
| 1.2 P&L Optimization | Calculates profit at every score cut-off to determine optimal approval strategy | `Cutoff_Optimization.py` / `03_Profit_Optimization_Curve.png` |
| 2.1 Limit Clustering | Runs K-Means clustering to segment customers and assign risk-adjusted credit limits | `Credit_Limit_Clustering.py` / `05_Customer_Segment_Profile_Plot.png` |
| 3.1 Monitoring ETL | Merges all model results and loads final data to `CreditPortfolioMonitor` table | `ETL_Portfolio_Setup.py` / 30 records confirmed in monitoring table |
| 3.2 Executive Reporting | Queries `CreditPortfolioMonitor` and generates executive dashboard visualization | `Viz_Dashboard_KPIs.py` / `06_Credit_Portfolio_Dashboard.png` |

---

## 1. Data Ingestion & Core SQL Analysis

Key findings from initial SQL queries (available in `04_Analysis_Outputs/`):

| Query | Key Finding |
|-------|------------|
| Max Days in Arrears | Customer **C002** recorded the highest delinquency at **8 days in arrears** |
| Fully Paid Off | **13** customers fully paid off their outstanding balance |
| Risk Band | All **30** customers are classified as 'Low' risk at final observation |
| Avg. Utilization | Portfolio-wide average utilization: **17.668%** |

### Insights from Raw SQL Analysis

- **Highest Risk Customers (Defaulters):** C002, C004, C008, C017, and C020 hit a delinquency ≥6 days; C002 peaked at 8 days.  
- **Highest Interest Paid:** C006 paid ₦1,416 and C013 paid ₦1,403, suggesting these loans had the largest balances or longest durations.  
- **Lowest Repayment Activity:** C017 recorded the lowest cumulative repayment (₦10,332) and is one of the highest risk customers (6 days in arrears).

---

## 2. Advanced Deliverables (Extra Credit)

### 2.1 Credit Risk Modeling & Explainability (Including P&L Optimization)

A Logistic Regression model was trained using cumulative repayment and interest to predict the binary target `Is_High_Risk` (`max_days_in_arrears > 5`).

| Metric | Result | Associated Risk |
|--------|--------|----------------|
| Optimal Score Cut-off | 601 | Highest profit achieved by approving customers with scores ≥601 |
| Max Expected Profit | ₦58,729 | Max profit at the optimal cut-off |
| Associated Default Rate | 6.67% | Targeted default rate to maximize P&L |

#### Model Explainability

| Feature | Coefficient | Directionality |
|---------|------------|----------------|
| cumulative_repayment | −0.000138 | **Strongest factor**. The negative coefficient confirms that higher repayment strongly decreases the probability of being classified as high-risk. |
| cumulative_interest | −0.000014 | Minor negative impact |

---

### 2.2 Advanced Financial Metric: Average Recovery Rate

| Advanced Metric | Definition | SQL Technique |
|-----------------|------------|---------------|
| Average Recovery Rate | % of original loan recovered from customers meeting default criteria | CTEs and advanced JOINs |

**Result:** 1.09326839 (109.33% of original loan amount)

**Interpretation:** Recovery over 100% indicates successful repayment of principal + accrued interest, demonstrating strong financial performance despite minor delinquency.

---

### 2.3 Data Visualization

| Visualization | Insight Communicated |
|---------------|--------------------|
| Max Arrears Histogram | Shows risk distribution of the portfolio; most customers cluster at low delinquency with few high-risk outliers |
| Portfolio Repayment Trend | Shows overall portfolio health over 60 days; steady negative slope confirms principal repayment efficiency |

---

## 3. Portfolio Monitoring & Executive Reporting

| risk_segment | total_customers_approved | portfolio_default_rate_pct | total_outstanding_exposure | avg_expected_pnl_per_customer |
|--------------|-------------------------|---------------------------|---------------------------|-------------------------------|
| Prime | 15 | 20.00% | ₦39,591.09 | ₦355.05 |
| High-Risk | 8 | 0.00% | ₦0.00 | ₦360.89 |
| Good | 4 | 25.00% | ₦0.00 | ₦359.29 |
| Average | 3 | 33.33% | ₦0.00 | ₦359.52 |

**Key Insight:** High-Risk segment shows 0.00% default rate but highest average expected P&L (₦360.89), warranting review of risk labeling.

---

## 4. Qualitative Analysis & Risk Metrics

| Topic | Metric / Strategy |
|-------|------------------|
| Portfolio Risk Over Time | Rolling Average Days in Arrears → leading indicator of portfolio quality deterioration |
| Outlier Identification | Z-score on Cumulative Interest / Repayment Ratio → identifies efficiency outliers |
| Repayment Structure | High Interest / Repayment Ratio → payments primarily servicing interest, not principal |
| Visualization | Cohort Analysis Line Chart → tracks average outstanding balance over time by loan characteristics |

---

## 5. Statistics & Data Interpretation (Qualitative Answers)

### Q1: Measuring the fastest repaying customers using utilization (%)

**Metric:** Rate of Change in Utilization (Steepest Negative Slope).

**Rationale:** The fastest customers are those who experience the largest drop in the `utilization (%)` metric over a defined period (e.g., weekly or monthly). This indicates the most aggressive principal reduction relative to the available credit.

### Q2: Interpreting a high Cumulative Interest / Cumulative Repayment ratio

**Interpretation:** This suggests an **adverse repayment structure** for the customer, where a higher proportion of their total payments is servicing the **interest** rather than reducing the **principal**.

**Implication:** The customer is likely making payments late, missing payments, or only paying the minimum required amount, allowing the interest to accrue heavily against a higher principal balance.

### Q3: Suggesting a visualization for repayment performance

**Visualization:** **Cohort Analysis** using a **Line Chart**.

**Implementation:** Group customers by a starting characteristic (e.g., initial loan size). Plot the **Average Outstanding Balance** (Y-axis) over **Days Since Loan Origination** (X-axis). The chart instantly shows which groups (lines) are driving the balance down most effectively.

### Q4: Identifying outliers in repayment behavior with thousands of customers

**Strategy:** A two-step statistical approach:
1.  **Risk Outliers:** Use a fixed threshold or a **Percentile-based filter (e.g., top 1%)** on the `MAX(days_in_arrears)` metric.
2.  **Efficiency Outliers:** Calculate the **Z-score** for the **Cumulative Interest / Cumulative Repayment Ratio**. Customers with a Z-score $> 3$ are statistically significant outliers with very poor repayment efficiency.

### Q5: Metric for evaluating portfolio risk over time

**Metric:** **Rolling Average Days in Arrears** (across all active customers).

**Rationale:** This provides a **leading indicator** of portfolio quality. A rising trend in the average days customers are late signals portfolio health deterioration, allowing the risk team to intervene proactively before arrears convert to significant losses.