import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
DATA_PATH = '04_Analysis_Outputs/'
MODEL_OUTPUT_PATH = '04_Analysis_Outputs/'
SCORE_INPUT_FILE = os.path.join(DATA_PATH, "Model_Scoring_Output.csv")
CLUSTER_VIS_FILENAME = "04_KMeans_Elbow_Plot.png"
SEGMENT_VIS_FILENAME = "05_Customer_Segment_Profile_Plot.png"
FINAL_OUTPUT_FILE = os.path.join(MODEL_OUTPUT_PATH, "Credit_Limit_Recommendations.csv")

# 1. Load Data 
try:
    df_base = pd.read_csv(SCORE_INPUT_FILE)[['customer_id']].copy()
except FileNotFoundError:
    print(f"Error: Base file not found: {SCORE_INPUT_FILE}.")
    exit()

# --- 2. Synthesize Complex Features for Clustering (The Feature Engineering Matrix) ---
N = len(df_base)
np.random.seed(42) 

df_base['avg_monthly_net_income'] = np.random.lognormal(mean=9.5, sigma=0.8, size=N).round(0)
df_base['income_volatility'] = np.random.beta(a=2, b=5, size=N) # Lower beta value means less volatile is better
df_base['avg_min_daily_balance'] = df_base['avg_monthly_net_income'] * np.random.uniform(0.05, 0.5, size=N) # Balance as % of income
df_base['max_days_in_arrears'] = np.random.poisson(lam=5, size=N)
df_base['prior_loan_count'] = np.random.randint(1, 15, size=N)
df_base.loc[df_base['max_days_in_arrears'] > 15, 'avg_monthly_net_income'] *= 0.5 # Correlate high arrears with lower income

# Select features for clustering
features = [
    'avg_monthly_net_income', 'income_volatility', 
    'avg_min_daily_balance', 'max_days_in_arrears', 
    'prior_loan_count'
]
X_cluster = df_base[features].copy()

# 3. Standardize Data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_cluster)
X_scaled_df = pd.DataFrame(X_scaled, columns=features)


# 4. Determine Optimal K (Elbow Method)
inertia = []
K_range = range(2, 11)
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)

# Plot the Elbow Curve
plt.figure(figsize=(8, 5))
plt.plot(K_range, inertia, marker='o', linestyle='-', color='purple')
plt.title('K-Means Elbow Method for Optimal K', fontsize=14)
plt.xlabel('Number of Clusters (K)', fontsize=12)
plt.ylabel('Inertia (Within-Cluster Sum of Squares)', fontsize=12)
plt.xticks(K_range)
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig(os.path.join(MODEL_OUTPUT_PATH, CLUSTER_VIS_FILENAME))
plt.close()
print(f"Elbow Method plot saved as {CLUSTER_VIS_FILENAME}")

# --- 5. Apply K-Means with Optimal K ---
# Based on a typical elbow plot shape, we often choose K=3 or K=4 for segmentation.
# We will use K=4 for better business stratification (Prime, Good, Average, High-Risk)
K = 4 
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
df_base['Cluster'] = kmeans.fit_predict(X_scaled)


# --- 6. Profile Clusters and Assign Limits ---

# Analyze the average feature values for each cluster
cluster_profile = df_base.groupby('Cluster')[features].mean().reset_index()

# Sort clusters to assign risk level (e.g., sort by max_days_in_arrears - ascending = lower risk)
cluster_profile = cluster_profile.sort_values(by='max_days_in_arrears', ascending=True).reset_index(drop=True)

# Assign Risk Labels and Base Limit Logic
risk_labels = {
    0: {'Label': 'Prime', 'Multiplier': 0.8},
    1: {'Label': 'Good', 'Multiplier': 0.6},
    2: {'Label': 'Average', 'Multiplier': 0.4},
    3: {'Label': 'High-Risk', 'Multiplier': 0.2} 
}

# The Recommended Limit is a percentage of the cluster's average net income
cluster_profile['Risk_Label'] = cluster_profile.index.map(lambda x: risk_labels[x]['Label'])
cluster_profile['Limit_Multiplier'] = cluster_profile.index.map(lambda x: risk_labels[x]['Multiplier'])
cluster_profile['Recommended_Base_Limit'] = (
    cluster_profile['avg_monthly_net_income'] * cluster_profile['Limit_Multiplier']
).round(0).astype(int)

# Map the final recommendations back to the original DataFrame
cluster_map = cluster_profile.set_index('Cluster')['Recommended_Base_Limit'].to_dict()
df_base['recommended_limit'] = df_base['Cluster'].map(cluster_map)

# Add Risk Label for final presentation
risk_label_map = cluster_profile.set_index('Cluster')['Risk_Label'].to_dict()
df_base['risk_segment'] = df_base['Cluster'].map(risk_label_map)


# --- 7. Final Output and Visualization ---

# Visualize the cluster profiles
cluster_profile_long = pd.melt(
    cluster_profile.drop(columns=['Recommended_Base_Limit', 'Limit_Multiplier']),
    id_vars=['Risk_Label', 'Cluster'], 
    var_name='Feature', 
    value_name='Average_Value'
)

plt.figure(figsize=(12, 7))
sns.barplot(
    x='Feature', 
    y='Average_Value', 
    hue='Risk_Label', 
    data=cluster_profile_long, 
    palette='viridis'
)
plt.title('Customer Segment Profiles (Driving Credit Limits)', fontsize=16)
plt.xlabel('Feature', fontsize=12)
plt.ylabel('Average Feature Value (Raw Scale)', fontsize=12)
plt.xticks(rotation=15)
plt.legend(title='Risk Segment')
plt.tight_layout()
plt.savefig(os.path.join(MODEL_OUTPUT_PATH, SEGMENT_VIS_FILENAME))
plt.close()
print(f"Cluster Segment Profile plot saved as {SEGMENT_VIS_FILENAME}")

# Save the final recommendations
final_output_df = df_base[['customer_id', 'risk_segment', 'recommended_limit']].copy()
final_output_df.to_csv(FINAL_OUTPUT_FILE, index=False)
print(f"\n--- Project 2 Complete ---")
print(f"Credit Limit Recommendations saved to: {FINAL_OUTPUT_FILE}")
print("\nRecommendation Example:")
print(final_output_df.head())