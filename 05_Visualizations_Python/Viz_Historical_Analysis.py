import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

# Set Matplotlib backend to save files without a display environment
matplotlib.use('Agg')

# --- 1. Setup & Connection ---

# Determine the absolute path to the project root directory
# This finds the current script's directory, goes up one level (05_Visualizations_Python), 
# and then up a second level (Kuda_Loan_Analysis_Project).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from the project root. This is secure.
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
ENCODED_PASSWORD = quote_plus(MYSQL_PASSWORD)

# Construct the full output path
OUTPUT_DIR = os.path.join(PROJECT_ROOT, '04_Analysis_Outputs')

mysql_url = (
    f'mysql+mysqlconnector://{MYSQL_USER}:{ENCODED_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
)

try:
    engine = create_engine(mysql_url)
    print("Connection established for visualization data pull.")
except Exception as e:
    print(f"FATAL ERROR: Could not connect to MySQL: {e}")
    exit()

# --- 2. Data Pull: Max Arrears (for Histogram) ---

# Query pulls the max arrears data for each customer
arrears_query = """
SELECT
    customer_id,
    MAX(days_in_arrears) AS max_days_in_arrears
FROM
    LoanSnapshot
GROUP BY
    customer_id;
"""
df_arrears = pd.read_sql(arrears_query, engine)

# --- 3. Data Pull: Outstanding Balance Trend (for Cohort Analysis) ---

# Query pulls all daily data for a visualization of the trend
trend_query = "SELECT `date`, outstanding_balance FROM LoanSnapshot ORDER BY `date`;"
df_trend = pd.read_sql(trend_query, engine)
df_trend['date'] = pd.to_datetime(df_trend['date']).dt.date

# --- 4. Visualization Functions ---

def create_arrears_histogram(df):
    """Generates a histogram of maximum days in arrears."""
    plt.figure(figsize=(10, 6))
    sns.histplot(df['max_days_in_arrears'], bins=range(int(df['max_days_in_arrears'].max()) + 2), kde=False, color='darkred', edgecolor='black')
    
    plt.title('Distribution of Maximum Days in Arrears (Risk Profile)', fontsize=14)
    plt.xlabel('Maximum Days in Arrears', fontsize=12)
    plt.ylabel('Number of Customers', fontsize=12)
    plt.xticks(range(int(df['max_days_in_arrears'].max()) + 1))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    file_path = os.path.join(OUTPUT_DIR, '01_Max_Arrears_Histogram.png')
    plt.savefig(file_path)
    plt.close()
    print(f"Saved: {file_path}")

def create_outstanding_balance_trend(df):
    """Generates a time series chart for the average outstanding balance."""
    # Calculate the average outstanding balance per date
    df_daily_avg = df.groupby('date')['outstanding_balance'].mean().reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='date', y='outstanding_balance', data=df_daily_avg, color='darkgreen', linewidth=2)
    
    plt.title('Portfolio Repayment Performance (Average Outstanding Balance Over Time)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Average Outstanding Balance', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    file_path = os.path.join(OUTPUT_DIR, '02_Portfolio_Repayment_Trend.png')
    plt.savefig(file_path)
    plt.close()
    print(f"Saved: {file_path}")

# --- 5. Execution ---

if __name__ == "__main__":
    print("--- Starting Visualization Generation ---")
    create_arrears_histogram(df_arrears)
    create_outstanding_balance_trend(df_trend)
    print("--- Visualization Complete ---")