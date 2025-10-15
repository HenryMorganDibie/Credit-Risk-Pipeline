import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy.sql import text 
# NEW: Import specific SQLAlchemy types for robust table creation
from sqlalchemy import Integer, DECIMAL 

# --- Configuration & Setup ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

DATA_PATH = '04_Analysis_Outputs/'
SCORE_FILE = os.path.join(DATA_PATH, "Model_Scoring_Output.csv")
LIMIT_FILE = os.path.join(DATA_PATH, "Credit_Limit_Recommendations.csv")
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
    print("Connection established for database loading.")
except Exception as e:
    print(f"FATAL ERROR: Could not connect to MySQL: {e}")
    exit()

# --- 1. Load and Merge Data from Projects 1 and 2 ---
df_scores = pd.read_csv(SCORE_FILE).rename(columns={'Is_High_Risk': 'actual_default'})
df_limits = pd.read_csv(LIMIT_FILE)

df_final = pd.merge(df_scores, df_limits, on='customer_id', how='inner')

# --- 2. Transformation (Simulate Real-Time Status & Financials) ---
np.random.seed(123) 

# Simulate Loan Status based on actual_default and segment
df_final['loan_status'] = np.select(
    [df_final['actual_default'] == 1, df_final['risk_segment'] == 'Prime'],
    ['Default', 'Active'],
    default='Settled'
)

# Simulate Days Past Due (DPD) - Correlated with risk
df_final['days_past_due'] = np.where(
    df_final['loan_status'] == 'Default', 
    np.random.randint(30, 90, len(df_final)), 
    0
)

# Simulate Outstanding Balance
df_final['outstanding_balance'] = np.where(
    df_final['loan_status'] == 'Active', 
    df_final['recommended_limit'] * np.random.uniform(0.1, 0.8, len(df_final)), 
    0
)
df_final['outstanding_balance'] = df_final['outstanding_balance'].round(2)

# Simplify P&L for monitoring (use the credit_score as a proxy for expected profitability)
df_final['expected_profit_loss'] = (df_final['credit_score'] / 700) * 1000 - 500
df_final['expected_profit_loss'] = df_final['expected_profit_loss'].round(2)


# --- 3. Load (L) into MySQL Database ---

try:
    print(f"Loading {len(df_final)} records into {DB_TABLE}...")
    
    # FIX: Using imported SQLAlchemy type objects for robustness
    df_final.to_sql(
        DB_TABLE, 
        con=engine, 
        if_exists='replace', 
        index=False,
        dtype={
            'credit_score': Integer, # Use SQLAlchemy Integer object
            'actual_default': Integer,
            'recommended_limit': Integer,
            'days_past_due': Integer,
            'outstanding_balance': DECIMAL(10, 2), # Use SQLAlchemy DECIMAL object
            'expected_profit_loss': DECIMAL(10, 2)
        }
    )
    print(f"SUCCESS: Data loaded into MySQL table '{DB_TABLE}'.")

except Exception as e:
    print(f"ERROR during data load: {e}")
    
# --- Final Check ---
if engine:
    try:
        with engine.connect() as conn:
            query = text(f"SELECT COUNT(*) FROM {DB_TABLE}")
            count = conn.execute(query).scalar()
            print(f"Verification: {count} records confirmed in the table.")
    except Exception as e:
        print(f"ERROR during verification query: {e}")