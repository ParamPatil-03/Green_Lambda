import os
import pandas as pd
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')

df = pd.read_csv(ORIG_DATA_FILE)
median_row = pd.DataFrame([df.median(numeric_only=True)])
print("--- FALLBACK (DATASET MEDIAN) VALUES ---")
print(f"aws_duration_ms: {median_row['aws_duration_ms'].values[0]}")
print(f"lines_of_code: {median_row['lines_of_code'].values[0]}")
print(f"cyclomatic_complexity: {median_row['cyclomatic_complexity'].values[0]}")
print(f"memory_config_mb: {median_row['memory_config_mb'].values[0]}")

# Simulate app.py logic
row = median_row.copy()
row['function_name'] = 'etl-transform-10'
row['function_type'] = df['function_type'].mode()[0]
row['input_size'] = df['input_size'].mode()[0]

def fval(col): return float(row[col].values[0])
def ival(col): return int(round(float(row[col].values[0])))

df_single = pd.DataFrame({
    'function_name': [df['function_name'].iloc[0]], # since etl-transform-10 not in df
    'function_type': [str(row['function_type'].values[0])],
    'input_size':    [str(row['input_size'].values[0])],
    'memory_config_mb':      [fval('memory_config_mb')],
    'cold_start':            [ival('cold_start')],
    'lines_of_code':         [fval('lines_of_code')],
    'num_loops':             [fval('num_loops')],
    'num_conditionals':      [fval('num_conditionals')],
    'num_function_calls':    [fval('num_function_calls')],
    'cyclomatic_complexity': [fval('cyclomatic_complexity')],
    'max_nesting_depth':     [fval('max_nesting_depth')],
    'local_duration_ms':     [fval('local_duration_ms')],
    'local_cpu_percent':     [fval('local_cpu_percent')],
    'local_memory_mb':       [fval('local_memory_mb')],
    'aws_duration_ms':       [fval('aws_duration_ms')],
    'aws_memory_used_mb':    [fval('aws_memory_used_mb')],
    'duration_ratio':        [fval('duration_ratio')],
    'memory_efficiency':     [fval('memory_efficiency')],
})

drop_cols = [c for c in ['energy_target_wh', 'local_energy_wh', 'aws_energy_estimate_wh', 'aws_cold_start'] if c in df.columns]
df_base = df.drop(columns=drop_cols)
if 'cold_start' in df_base.columns:
    df_base['cold_start'] = pd.to_numeric(df_base['cold_start'], errors='coerce').fillna(0).astype(int)

df_temp = pd.concat([df_base, df_single], ignore_index=True)
df_encoded = pd.get_dummies(df_temp, columns=['function_name', 'function_type', 'input_size'], drop_first=True)
X_single = df_encoded.iloc[[-1]].copy()

MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')
feat_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
with open(feat_path, 'rb') as f:
    feature_names = pickle.load(f)
feature_names = [f for f in feature_names if f != 'calibration_ratio']

for col in feature_names:
    if col not in X_single.columns:
        X_single[col] = 0

X_single = X_single[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0)

with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'rb') as f:
    xgb_model = pickle.load(f)
    
energy_pred = float(xgb_model.predict(X_single)[0])
print(f"\nEnergy Prediction (Pure Fallback, no live override): {energy_pred:.6f}")

# Now add live overrides
X_single['aws_duration_ms'] = 3.656888888888889
X_single['lines_of_code'] = 39.0
X_single['cyclomatic_complexity'] = 7.0

energy_pred_live = float(xgb_model.predict(X_single)[0])
print(f"Energy Prediction (Fallback + Live Overrides): {energy_pred_live:.6f}")
