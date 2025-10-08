import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
from dotenv import load_dotenv 
import os 
from urllib.parse import quote_plus

# --- Load environment variables from .env file ---
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# --- 1. Database Connection Details (NOW LOADED SECURELY) ---
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE') 

# --- 2. Read the Excel File into a DataFrame ---

# FIX 1: Define the path relative to the project root (where the pipeline runs from)
INPUT_DIR = '01_Data_Input'
EXCEL_FILE_NAME = 'Loan_Snapshot_Interview_Dataset.xlsx'

# Construct the path relative to the current working directory (project root)
excel_file_path = os.path.join(INPUT_DIR, EXCEL_FILE_NAME)

try:
    print(f"Attempting to load data from: {os.path.join(os.getcwd(), excel_file_path)}")
    df = pd.read_excel(excel_file_path)
    print(f"Read {len(df)} rows from Excel.")
except FileNotFoundError:
    print(f"ERROR: Excel file not found at {excel_file_path}. Please verify the file is in the 01_Data_Input folder.")
    exit()


# --- 3. Clean Column Names for SQL ---
# Rename the column with the special character
df.rename(columns={'utilization (%)': 'utilization_pct'}, inplace=True)

# --- 4. Establish SQL Connection (using SQLAlchemy) ---
# Check for credentials before attempting connection
if not all([MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE]):
    print("ERROR: Database credentials missing or incomplete. Check your .env file.")
    exit()

# 4.1 URL ENCODE THE PASSWORD to handle special characters (like @ or !)
ENCODED_PASSWORD = quote_plus(MYSQL_PASSWORD)

# 4.2 Construct the URL using the ENCODED password
mysql_url = (
    f'mysql+mysqlconnector://{MYSQL_USER}:{ENCODED_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}'
)

try:
    engine = create_engine(mysql_url)
    print("Attempting to connect to MySQL...")
    
    # --- 5. Load the DataFrame into MySQL ---
    # FIX 2: Use lowercase table name to prevent MySQL case sensitivity errors.
    df.to_sql(
        name='loansnapshot', 
        con=engine, 
        if_exists='replace', 
        index=False
    )
    
    print("--------------------------------------------------------")
    print(f"SUCCESS: Data loaded into the 'loansnapshot' table in {MYSQL_DATABASE}!")

except Exception as e:
    print("--------------------------------------------------------")
    print(f"FATAL ERROR: Could not load data into MySQL.")
    print(f"Details: {e}")