import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# --- Configuration (Based on your project structure) ---
DATA_PATH = '04_Analysis_Outputs/'
SCORE_INPUT_FILE = os.path.join(DATA_PATH, "Model_Scoring_Output.csv")
OUTPUT_PATH = '04_Analysis_Outputs/'
VIS_FILENAME = "03_Profit_Optimization_Curve.png"

# --- 1. Load the Model Score Output ---
try:
    df = pd.read_csv(SCORE_INPUT_FILE)
    # Rename 'Is_High_Risk' to 'actual_default' for clearer P&L context
    df = df.rename(columns={'Is_High_Risk': 'actual_default'})
except FileNotFoundError:
    print(f"Error: Required file not found: {SCORE_INPUT_FILE}.")
    print("Please ensure your 03_Model_Training.py script was run and created this file.")
    exit()

# Ensure the score is an integer
df['credit_score'] = df['credit_score'].astype(int)

# --- 2. Simulate Financial Outcomes (The P&L Bridge) ---
# This is the synthetic data needed for a P&L analysis, anchored to your real scores.
np.random.seed(42)

# Simulate loan amount: Higher score customers are offered larger loans (Higher potential profit/loss)
df['loan_amount'] = np.where(
    df['credit_score'] >= 650, 
    np.random.randint(50000, 250000, size=len(df)), # Larger loans for high scores
    np.random.randint(10000, 70000, size=len(df))   # Smaller loans for low scores
)

INTEREST_RATE = 0.15      # 15% interest/fees for a quick loan (Revenue)
COLLECTION_RATE = 0.20    # 20% of revenue collected even if the customer defaults

df['revenue'] = df['loan_amount'] * INTEREST_RATE

# Calculate Net Profit/Loss (The P&L formula):
# If default (1): Loss = -(Principal) + (Partial Revenue Collected)
# If no default (0): Profit = (Full Revenue)
df['net_profit_loss'] = np.where(
    df['actual_default'] == 1,
    -df['loan_amount'] + (df['revenue'] * COLLECTION_RATE), 
    df['revenue']
)

# --- 3. Optimization Analysis (Part B: Calculate Metrics per Cut-off) ---

# Define the Range of Cut-offs to Analyze (Min score to Max score in 5-point steps)
score_min = df['credit_score'].min()
score_max = df['credit_score'].max()
score_cutoffs = np.arange(score_min, score_max, 5)

total_applications = len(df)
results = []

for cutoff in score_cutoffs:
    # Filter for Approved Customers
    approved_df = df[df['credit_score'] >= cutoff].copy()
    if approved_df.empty:
        continue
    
    # Calculate Key Metrics
    total_approved = len(approved_df)
    approval_rate = (total_approved / total_applications) * 100
    defaults = approved_df['actual_default'].sum()
    default_rate = (defaults / total_approved) * 100
    total_pnl = approved_df['net_profit_loss'].sum()
    
    results.append({
        'Cut_off_Score': cutoff,
        'Approval_Rate': round(approval_rate, 2),
        'Default_Rate': round(default_rate, 2),
        'Total_Expected_Profit': round(total_pnl, 0)
    })

optimization_df = pd.DataFrame(results)
optimization_df.set_index('Cut_off_Score', inplace=True)


# --- 4. Visualization and Recommendation (Part C) ---

# Find the optimal point (where profit is maximized)
optimal_score = optimization_df['Total_Expected_Profit'].idxmax()
optimal_point = optimization_df.loc[optimal_score]

# --- Visualization: Risk-Reward Trade-Off Curve ---
fig, ax1 = plt.subplots(figsize=(12, 6))
sns.set_style("whitegrid")

# Primary Y-Axis: Total Expected Profit
color = '#0056b3' # Kuda Blue
ax1.set_xlabel('Score Cut-off Threshold', fontsize=12)
ax1.set_ylabel('Total Expected Profit ($)', color=color, fontsize=12)
ax1.bar(optimization_df.index, optimization_df['Total_Expected_Profit'], color=color, alpha=0.6, width=4)
ax1.tick_params(axis='y', labelcolor=color)

# Annotation for Optimal Point
ax1.axvline(x=optimal_score, color='red', linestyle='--', linewidth=2, label=f'Optimal Cut-off: {optimal_score}')

# Secondary Y-Axis: Approval Rate and Default Rate
ax2 = ax1.twinx()  
color_ap = 'darkgreen'
color_dr = 'darkred'
ax2.set_ylabel('Rate (%)', fontsize=12)  

# Approval Rate Line
ax2.plot(optimization_df.index, optimization_df['Approval_Rate'], label='Approval Rate (%)', color=color_ap, linewidth=2, marker='o', markersize=4)

# Default Rate Line
ax2.plot(optimization_df.index, optimization_df['Default_Rate'], label='Default Rate (%)', color=color_dr, linestyle='--', linewidth=2, marker='^', markersize=4)

ax2.tick_params(axis='y')

# Title and Legend
plt.title('Credit Strategy Optimization: Risk-Reward Trade-Off Curve', fontsize=16, weight='bold')
fig.tight_layout()
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))

# Save the figure
plt.savefig(os.path.join(OUTPUT_PATH, VIS_FILENAME))
plt.close()
print(f"\nOptimization Visualization saved as {os.path.join(OUTPUT_PATH, VIS_FILENAME)}")


# --- Strategic Output ---
print("\n--- Strategic Recommendation for Kuda Credit Team ---")
print(f"**Optimal Score Cut-off:** {int(optimal_score)}")
print(f"**Max Expected Profit:** ${optimal_point['Total_Expected_Profit']:,.0f} (at this cut-off)")
print(f"**Associated Approval Rate:** {optimal_point['Approval_Rate']}%")
print(f"**Associated Default Rate:** {optimal_point['Default_Rate']}%")
print("\nRecommendation: This cut-off maximizes the return on the credit portfolio. It should be validated via an A/B test before full deployment.")