# Kuda Loan Analysis Project (Data Engineering & Portfolio Risk)

## Project Overview

This project simulates a data engineering and financial analysis pipeline designed to load, organize, and analyze a loan snapshot dataset. The goal is to calculate key portfolio risk metrics and provide analytical interpretations of customer repayment behavior. This project showcases proficiency in **Python data handling, secure credential management, advanced SQL querying, Credit Risk Modeling, and end-to-end workflow automation.**

**Key Technologies Used:**
- **Python/Pandas:** Data manipulation, Machine Learning (Logistic Regression).
- **SQLAlchemy/MySQL Connector:** Database connection and data ingestion.
- **MySQL/SQL:** Complex data querying (using CTEs, Window Functions, Aggregation).
- **Automation (PowerShell):** Sequential pipeline execution for MLOps simulation.
- **Matplotlib/Seaborn:** Data visualization.

## Project Structure

The project is organized into a clean, reproducible folder structure:

- **`01_Data_Input/`**: Contains the source Excel data (`Loan_Snapshot_Interview_Dataset.xlsx`).
- **`02_Scripts_Python/`**: Contains core logic:
    - `data_loader_excel_to_mysql.py` (Data ingestion)
    - **`train_credit_risk_model.py` (Credit risk model training and explainability)**
- **`03_Scripts_MySQL/`**: Contains all SQL query source code (`loan_snapshot_queries.sql`).
- **`04_Analysis_Outputs/`**: Contains the final analytical results (as CSV files and PNG visualizations).
- **`05_Visualizations_Python/`**: Contains the visualization script (`visualize_analysis.py`).
- **`run_pipeline.ps1`**: **Master PowerShell script for end-to-end pipeline automation.**
- **`.env`**: (Ignored by Git) Stores database connection credentials securely.

---

## Pipeline Automation & Execution

The entire analytical and modeling workflow is orchestrated via a single **PowerShell script (`run_pipeline.ps1`)** to demonstrate a reproducible, production-ready workflow. This aligns with experience in automation and ensures that data ingestion, ETL, risk modeling, and visualization all run sequentially on demand.

**Execution Flow (Triggered by `.\run_pipeline.ps1`):**
1.  **`data_loader_excel_to_mysql.py`**: Reads source data, performs cleaning, and loads data into the `loansnapshot` table in MySQL.
2.  **`loan_snapshot_queries.sql`**: Executes all core and advanced SQL queries, outputting aggregated CSVs.
3.  **`train_credit_risk_model.py`**: Consumes CSVs, trains the Logistic Regression model, and outputs feature coefficients/plots.
4.  **`visualize_analysis.py`**: Generates final PNG charts from SQL and ML outputs.

---

## 1. Data Ingestion & Core SQL Analysis

The data was successfully loaded into the `LoanDataAnalysis` database and queried to produce the following key findings (results are available in the `04_Analysis_Outputs/` folder):

| Query | Key Finding from `04_Analysis_Outputs/` |
| :--- | :--- |
| **Max Days in Arrears** | Customer **C002** recorded the highest delinquency at **8 days in arrears**. |
| **Fully Paid Off** | A total of **13** customers fully paid off their outstanding balance by the end of the period. |
| **Risk Band** | All **30** customers are classified as 'Low' risk at the final observation date. |
| **Avg. Utilization** | The portfolio-wide average utilization was **17.668%** at the end of the period. |

### Insights from Raw Data Files

The raw aggregation and arrears data provided immediate, actionable insights:
* **Highest Risk Customers (Defaulters):** Five customers (C002, C004, C008, C017, and C020) hit the highest delinquency level of **6 days or more in arrears**, with Customer **C002** hitting the peak at **8 days**. This segment represents the highest risk for future write-offs.
* **Highest Interest Paid:** Customer **C006** paid the highest cumulative interest at **₦1,416**, followed closely by C013 at **₦1,403**. This suggests these loans may have been active the longest or had the largest original balance, maximizing the interest collected.
* **Lowest Repayment Activity:** Customer **C017** recorded the lowest cumulative repayment at **₦10,332**. Interestingly, C017 is also one of the highest risk customers (6 days in arrears).

---

## 2. Advanced Deliverables (Extra Credit)

### 2.1 Credit Risk Modeling & Explainability

To demonstrate core skills in credit risk modeling, a Logistic Regression model was trained using key features (cumulative repayment and interest) to predict the binary target `Is_High_Risk` ($\text{max\_days\_in\_arrears} > 5$).

| Metric | Model | Feature Explainability | Output Files |
| :--- | :--- | :--- | :--- |
| **Prediction** | Logistic Regression | Model coefficients were analyzed to determine feature importance and directionality. | `ML_Coefficient_Feature_Importance.png` and `ML_Model_Coefficients.csv` |

**Key Finding:**
The **`cumulative\_repayment`** feature was found to be the dominant factor in risk prediction (Coefficient: **$-0.000138$**). The **negative coefficient** confirms that for every **₦1 increase in cumulative repayment**, the probability of being classified as high-risk decreases. This validates the model's intuitive financial logic.

### 2.2 Advanced Financial Metric: Average Recovery Rate

To demonstrate advanced financial modeling and complex SQL capabilities, we calculated the **Average Recovery Rate** for customers who met the internal definition of default.

| Advanced Metric | Definition | SQL Technique |
| :--- | :--- | :--- |
| **Average Recovery Rate** | The average percentage of the original loan amount recovered from customers who hit a high delinquency level. | **CTE (Common Table Expressions)** and Advanced JOINs |

**Result from `04_Analysis_Outputs/Advanced Metric, Average Recovery Rate for Defaulters.csv`:** **$1.09326839$** (or **$109.33\%$** of original loan amount).

**Interpretation:** A recovery rate over $100\%$ indicates that the metric captures the successful repayment of both the **principal** and the **accrued interest** for this cohort, suggesting strong financial performance despite minor delinquency events based on the original **₦** loan amount.

### 2.3 Data Visualization

To showcase advanced skills in data storytelling, the following charts were generated using Python (Matplotlib/Seaborn) and saved as PNG files in the `04_Analysis_Outputs/` folder:

| Visualization | Insight Communicated |
| :--- | :--- |
| **Max Arrears Histogram** | Shows the **Risk Distribution** of the portfolio. This chart makes it immediately clear that most customers are clustered at low delinquency, with only a few outliers hitting the highest risk bands. |
| **Portfolio Repayment Trend** | Shows the **Overall Portfolio Health** over the 60 days. The steady, consistent negative slope confirms that the portfolio as a whole is effectively paying down the principal balance. |

---

## 3. Statistics & Data Interpretation (Qualitative Answers)

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