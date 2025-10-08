import pandas as pd
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
import os

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# --- Configuration ---
# Assuming the script runs from the project root and files are in 04_Analysis_Outputs/
DATA_PATH = '04_Analysis_Outputs/'
MODEL_OUTPUT_PATH = '04_Analysis_Outputs/' 
# NOTE: The merged file was created in a previous step, adjust path if necessary.
try:
    df_merged = pd.read_csv(os.path.join(DATA_PATH, "ML_Credit_Risk_Data.csv"))
except FileNotFoundError:
    # Fallback plan if ML_Credit_Risk_Data.csv isn't found
    df_agg = pd.read_csv(os.path.join(DATA_PATH, "Aggregation, Total Cumulative Repayment and Interest at Final Day.csv"))
    df_arrears = pd.read_csv(os.path.join(DATA_PATH, "Arrears Tracking, Maximum Days in Arrears Observed.csv"))
    df_merged = pd.merge(df_agg, df_arrears, on='customer_id')
    # Target: 1 if max_days_in_arrears > 5 (High Risk), 0 otherwise
    df_merged['Is_High_Risk'] = np.where(df_merged['max_days_in_arrears'] > 5, 1, 0)
    df_merged.to_csv(os.path.join(MODEL_OUTPUT_PATH, "ML_Credit_Risk_Data.csv"), index=False)


# 1. Define Features and Target
features = ['cumulative_repayment', 'cumulative_interest']
X = df_merged[features]
y = df_merged['Is_High_Risk']

# 2. Train the Logistic Regression Model
# Logistic Regression is a standard, interpretable credit risk model
model = LogisticRegression(solver='liblinear', random_state=42)
model.fit(X, y)

# 3. Extract and analyze Coefficients for Explainability
coefficients = model.coef_[0]
intercept = model.intercept_[0]

# Create a DataFrame for Model Explainability
feature_importance = pd.DataFrame({
    'Feature': features,
    'Coefficient': coefficients,
    'Abs_Coefficient': np.abs(coefficients) # Absolute value shows magnitude of importance
}).sort_values(by='Abs_Coefficient', ascending=False).reset_index(drop=True)

# 4. Generate a Feature Importance Bar Plot (based on coefficient magnitude)
plt.figure(figsize=(8, 5))
sns.barplot(
    x='Abs_Coefficient', 
    y='Feature', 
    data=feature_importance, 
    palette='magma'
)
plt.title('Feature Importance (Logistic Regression Coefficients)', fontsize=14)
plt.xlabel('Absolute Coefficient Value', fontsize=12)
plt.ylabel('Feature', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(MODEL_OUTPUT_PATH, "ML_Coefficient_Feature_Importance.png"))
plt.close()

# 5. Save the coefficients table for documentation
feature_importance_output = feature_importance[['Feature', 'Coefficient']].copy()
feature_importance_output.to_csv(os.path.join(MODEL_OUTPUT_PATH, "ML_Model_Coefficients.csv"), index=False)

print("--- ML Step Complete (Model Training & Explainability) ---")
print(f"Model Intercept (Bias): {intercept:.4f}")
print("Coefficients Table saved as 04_Analysis_Outputs/ML_Model_Coefficients.csv")
print("Feature Importance Plot saved as 04_Analysis_Outputs/ML_Coefficient_Feature_Importance.png")
print("\nCoefficient Analysis:")
print(feature_importance_output)