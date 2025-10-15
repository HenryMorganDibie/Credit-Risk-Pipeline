import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# Set Matplotlib backend to save files without a display environment
matplotlib.use('Agg')

# --- Configuration & Setup ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

MODEL_OUTPUT_PATH = '04_Analysis_Outputs/'
DASHBOARD_VIS_FILENAME = "06_Credit_Portfolio_Dashboard.png"
DB_TABLE = 'CreditPortfolioMonitor'

# MySQL connection details
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
ENCODED_PASSWORD = quote_plus(MYSQL_PASSWORD)

mysql_url = (
    f'mysql+mysqlconnector://{MYSQL_USER}:{ENCODED_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
)

try:
    engine = create_engine(mysql_url)
    print("Connection established for dashboard data pull.")
except Exception as e:
    print(f"FATAL ERROR: Could not connect to MySQL: {e}")
    exit()

# --- 1. Define the SQL Monitoring Query ---
# Note: This query calculates KPIs per segment
MONITORING_QUERY = f"""
SELECT
    risk_segment,
    COUNT(customer_id) AS total_customers_approved,
    (SUM(CASE WHEN loan_status = 'Default' THEN 1 ELSE 0 END) * 100.0 / COUNT(customer_id)) AS portfolio_default_rate_pct,
    SUM(outstanding_balance) AS total_outstanding_exposure,
    AVG(expected_profit_loss) AS avg_expected_pnl_per_customer
FROM
    {DB_TABLE}
GROUP BY 1
ORDER BY portfolio_default_rate_pct DESC;
"""

# --- 2. Data Pull and Preparation ---
try:
    df_dashboard = pd.read_sql(MONITORING_QUERY, engine)
    
    # Sort for cleaner visualization (e.g., Prime -> High-Risk)
    risk_order = ['Prime', 'Good', 'Average', 'High-Risk']
    df_dashboard['risk_segment'] = pd.Categorical(df_dashboard['risk_segment'], categories=risk_order, ordered=True)
    df_dashboard = df_dashboard.sort_values('risk_segment')
    
except Exception as e:
    print(f"ERROR: Could not pull monitoring data from MySQL: {e}")
    exit()

# --- 3. Visualization: Executive Dashboard (3 KPIs) ---

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
sns.set_style("whitegrid")
segment_colors = sns.color_palette("viridis", n_colors=len(df_dashboard))

# --- Plot 1: Portfolio Default Rate (%) ---
sns.barplot(
    ax=axes[0], 
    x='risk_segment', 
    y='portfolio_default_rate_pct', 
    data=df_dashboard, 
    palette=segment_colors
)
axes[0].set_title('KPI 1: Default Rate by Segment (%)', fontsize=14)
axes[0].set_ylabel('Default Rate (%)', fontsize=12)
axes[0].set_xlabel('ML Segment', fontsize=12)
axes[0].tick_params(axis='x', rotation=15)
axes[0].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter())


# --- Plot 2: Total Outstanding Exposure ---
sns.barplot(
    ax=axes[1], 
    x='risk_segment', 
    y='total_outstanding_exposure', 
    data=df_dashboard, 
    palette=segment_colors
)
axes[1].set_title('KPI 2: Total Exposure by Segment ($)', fontsize=14)
axes[1].set_ylabel('Total Outstanding Exposure', fontsize=12)
axes[1].set_xlabel('ML Segment', fontsize=12)
axes[1].tick_params(axis='x', rotation=15)
axes[1].ticklabel_format(style='plain', axis='y') # Use plain numbers for currency

# --- Plot 3: Average Expected Profitability ---
sns.barplot(
    ax=axes[2], 
    x='risk_segment', 
    y='avg_expected_pnl_per_customer', 
    data=df_dashboard, 
    palette=segment_colors
)
axes[2].set_title('KPI 3: Avg Expected P&L per Customer ($)', fontsize=14)
axes[2].set_ylabel('Avg Expected P&L', fontsize=12)
axes[2].set_xlabel('ML Segment', fontsize=12)
axes[2].tick_params(axis='x', rotation=15)


fig.suptitle('Executive Credit Portfolio Health Check (Driven by ML Segmentation)', fontsize=18, weight='bold', y=1.02)
plt.tight_layout(rect=[0, 0, 1, 0.98])

# Save the figure
file_path = os.path.join(MODEL_OUTPUT_PATH, DASHBOARD_VIS_FILENAME)
plt.savefig(file_path)
plt.close()

print("\n--- Project 3 Complete ---")
print(f"Executive Portfolio Dashboard saved to: {file_path}")
print("\nFinal Portfolio Health Check Data:")
print(df_dashboard)