# run_pipeline.ps1
# Master script for executing the Kuda Loan Analysis data pipeline end-to-end.
# This script simulates a production scheduler or CI/CD job by running steps sequentially
# and stopping if any script returns an error.

$ErrorActionPreference = "Stop" # Stop the script immediately on error

Write-Host "--- Kuda Loan Analysis Pipeline Started ---" -ForegroundColor Yellow
Write-Host "Ensuring virtual environment is active..."

# NOTE: This assumes your 'python' executable points to the correct virtual environment (e.g., via '.\.venv\Scripts\Activate.ps1').

try {
    # 1. DATA INGESTION: Load data from Excel, clean, and populate MySQL tables.
    Write-Host "`n[STEP 1/3] Running Data Ingestion and ETL..." -ForegroundColor Cyan
    python 02_Scripts_Python\data_loader_excel_to_mysql.py
    # NOTE: This script is also where the core SQL analysis (03_Scripts_MySQL/loan_snapshot_queries.sql)
    # is often executed via Python and saved to CSVs.

    # 2. ML MODELING & EXPLAINABILITY: Train the risk model and generate coefficients.
    Write-Host "`n[STEP 2/3] Running Credit Risk Model Training..." -ForegroundColor Cyan
    python 02_Scripts_Python\train_credit_risk_model.py

    # 3. DATA VISUALIZATION: Generate final charts (PNGs).
    Write-Host "`n[STEP 3/3] Running Final Visualizations..." -ForegroundColor Cyan
    # Replace 'visualize_analysis.py' with your actual visualization script name if it is different
    python 05_Visualizations_Python\visualize_analysis.py

    # Final Success Message
    Write-Host "`n--- Pipeline Execution Complete! ---" -ForegroundColor Green
    Write-Host "All outputs (CSVs, PNGs) are available in the 04_Analysis_Outputs/ folder." -ForegroundColor Green

} catch {
    Write-Error "`n[PIPELINE FAILED] An error occurred during execution." -ForegroundColor Red
    Write-Host "Please check the error output above for details." -ForegroundColor Red
    exit 1
}