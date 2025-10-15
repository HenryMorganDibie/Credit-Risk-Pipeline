# run_pipeline.ps1
# Master script for executing the Kuda Loan Analysis data pipeline end-to-end.
# This script simulates a production scheduler or CI/CD job by running steps sequentially
# and stopping if any script returns an error.

$ErrorActionPreference = "Stop" # Stop the script immediately on error
$PythonScriptsPath = "02_Scripts_Python"
$VizScriptsPath = "05_Visualizations_Python"

Write-Host "--- Kuda Loan Analysis Pipeline Started ---" -ForegroundColor Yellow

try {
    # --- PHASE 0: DATA INGESTION & SQL ANALYSIS ETL ---
    Write-Host "`n[PHASE 0: Data Ingestion & SQL Analysis ETL]..." -ForegroundColor Magenta
    
    # 0.1 DATA INGESTION: Load data from Excel, clean, populate MySQL, and run core feature generation queries.
    Write-Host "  -> Running Data Ingestion, ETL, and Core SQL Analysis..." -ForegroundColor Cyan
    python "$PythonScriptsPath\data_loader_excel_to_mysql.py"
    
    # 0.2 INITIAL VIZ: Generate initial historical charts (Max Arrears, Repayment Trend).
    Write-Host "  -> Running Foundational Analysis Visualizations (Max Arrears, Trend)..." -ForegroundColor Cyan
    python "$VizScriptsPath\Viz_Historical_Analysis.py"
    
    # --- PHASE 1: CREDIT SCORING & PROFIT OPTIMIZATION (Project 1) ---
    Write-Host "`n[PHASE 1: Scoring & P&L Optimization]..." -ForegroundColor Magenta
    
    # 1.1 MODEL TRAINING: Train the Logistic Regression model, generate scores, and save output.
    # USING YOUR FILE NAME: Model_Training_V2_Scoring.py
    Write-Host "  -> Running Credit Score Generation (Project 1, Step 1)..." -ForegroundColor Cyan
    python "$PythonScriptsPath\Model_Training_V2_Scoring.py"
    
    # 1.2 OPTIMIZATION: Use scores to calculate P&L and determine optimal cut-off.
    # USING YOUR FILE NAME: Cutoff_Optimization.py
    Write-Host "  -> Running Strategic Cut-off Optimization (Project 1, Step 2)..." -ForegroundColor Cyan
    python "$PythonScriptsPath\Cutoff_Optimization.py"

    # --- PHASE 2: CREDIT LIMIT STRATEGY (Project 2) ---
    Write-Host "`n[PHASE 2: Limit Recommendation Strategy]..." -ForegroundColor Magenta

    # 2.1 CLUSTERING: Segment customers using K-Means and recommend limits.
    # USING YOUR FILE NAME: Credit_Limit_Clustering.py
    Write-Host "  -> Running Credit Limit Clustering (Project 2)..." -ForegroundColor Cyan
    python "$PythonScriptsPath\Credit_Limit_Clustering.py"

    # --- PHASE 3: PORTFOLIO MONITORING & REPORTING (Project 3) ---
    Write-Host "`n[PHASE 3: Portfolio Monitoring & Reporting]..." -ForegroundColor Magenta

    # 3.1 ETL LOAD: Merge all outputs and load the final monitoring table to MySQL.
    # USING YOUR FILE NAME: ETL_Portfolio_Setup.py
    Write-Host "  -> Running ETL to Load Monitoring Table to MySQL (Project 3, Step 1)..." -ForegroundColor Cyan
    python "$PythonScriptsPath\ETL_Portfolio_Setup.py"
    
    # 3.2 DASHBOARD: Connect to MySQL, execute the monitoring query, and generate the final dashboard.
    # USING YOUR PATH: 05_Visualizations_Python\Viz_Dashboard_KPIs.py
    Write-Host "  -> Running Executive Dashboard Visualization (Project 3, Step 2)..." -ForegroundColor Cyan
    python "$VizScriptsPath\Viz_Dashboard_KPIs.py"

    # Final Success Message
    Write-Host "`n--- Pipeline Execution Complete! ---" -ForegroundColor Green
    Write-Host "All strategic deliverables (CSVs, PNGs) are available in the 04_Analysis_Outputs/ folder." -ForegroundColor Green

} catch {
    Write-Error "`n[PIPELINE FAILED] An error occurred during execution in step: $($_.ScriptStackTrace.Split([Environment]::NewLine)[0])." -ForegroundColor Red
    Write-Host "Please check the error output above for details." -ForegroundColor Red
    exit 1
}
