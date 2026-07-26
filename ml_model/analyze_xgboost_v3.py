import os
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')
NEW_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'new_ml_dataset.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')

# Load datasets
df_orig = pd.read_csv(ORIG_DATA_FILE)
df_new = pd.read_csv(NEW_DATA_FILE)
df = pd.concat([df_orig, df_new], ignore_index=True)

df['energy_target_wh_v3'] = (10.0 + 0.2 * df['memory_config_mb']) * (df['aws_duration_ms'] / 3600000.0)

feat_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
with open(feat_path, 'rb') as f:
    feature_names = pickle.load(f)
feature_names = [f for f in feature_names if f != 'calibration_ratio']

df_encoded = pd.get_dummies(df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)
for col in feature_names:
    if col not in df_encoded.columns:
        df_encoded[col] = 0.0

X = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)
y = df_encoded['energy_target_wh_v3']

# Same split to get test indices
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load XGBoost model
with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'rb') as f:
    xgb_model = pickle.load(f)

# Predict
y_pred = xgb_model.predict(X_test)

# Map back to original dataframe to get memory and duration
test_indices = X_test.index
test_df = df.iloc[test_indices].copy()
test_df['y_true'] = y_test
test_df['y_pred'] = y_pred

# Helper function to compute metrics
def compute_metrics(subset):
    if len(subset) == 0:
        return np.nan, np.nan, np.nan, 0
    rmse = np.sqrt(mean_squared_error(subset['y_true'], subset['y_pred']))
    mae = mean_absolute_error(subset['y_true'], subset['y_pred'])
    r2 = r2_score(subset['y_true'], subset['y_pred']) if len(subset) > 1 else np.nan
    return rmse, mae, r2, len(subset)

print("=== Memory Tier Breakdown ===")
memory_tiers = [128, 256, 512, 1024, 2048, 3000]
print(f"{'Memory (MB)':<12} | {'n':<6} | {'RMSE':<10} | {'MAE':<10} | {'R2':<10}")
print("-" * 55)
for mem in memory_tiers:
    subset = test_df[test_df['memory_config_mb'] == mem]
    rmse, mae, r2, n = compute_metrics(subset)
    print(f"{mem:<12} | {n:<6} | {rmse:<10.6f} | {mae:<10.6f} | {r2:<10.4f}")

print("\n=== Duration Bucket Breakdown ===")
# Duration in seconds
test_df['duration_s'] = test_df['aws_duration_ms'] / 1000.0

bins = [0, 1, 10, 30, 67, np.inf]
labels = ['<1s', '1-10s', '10-30s', '30-67s', '>67s']
test_df['duration_bucket'] = pd.cut(test_df['duration_s'], bins=bins, labels=labels, right=False)

print(f"{'Duration':<12} | {'n':<6} | {'RMSE':<10} | {'MAE':<10} | {'R2':<10}")
print("-" * 55)
for bucket in labels:
    subset = test_df[test_df['duration_bucket'] == bucket]
    rmse, mae, r2, n = compute_metrics(subset)
    if n > 0:
        print(f"{bucket:<12} | {n:<6} | {rmse:<10.6f} | {mae:<10.6f} | {r2:<10.4f}")
