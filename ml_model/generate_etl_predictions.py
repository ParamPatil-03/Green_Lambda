import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')
NEW_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'new_ml_dataset.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')

# Load datasets
df_orig = pd.read_csv(ORIG_DATA_FILE)
df_new = pd.read_csv(NEW_DATA_FILE)
df = pd.concat([df_orig, df_new], ignore_index=True)

# Find etl-transform-10
target_func = 'etl-transform-10'
func_rows = df[df['function_name'] == target_func]

if len(func_rows) == 0:
    print(f"Error: {target_func} not found in the dataset!")
    exit(1)

row = func_rows.iloc[0]

print("Function Details:")
print(f"Name: {row['function_name']}")
print(f"Type (Category): {row['function_type']}")
print(f"Memory: {row['memory_config_mb']} MB")
print(f"Duration: {row['aws_duration_ms']} ms")
print("-" * 30)

# Function to extract features, encode, and predict
def predict_row(row_series):
    feat_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
    with open(feat_path, 'rb') as f:
        feature_names = pickle.load(f)
    feature_names = [f for f in feature_names if f != 'calibration_ratio']
    
    row_df = pd.DataFrame([row_series])
    df_encoded = pd.get_dummies(row_df, columns=['function_name', 'function_type', 'input_size'], drop_first=False)
    
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0.0
            
    X = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)
    
    with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'rb') as f:
        xgb_model = pickle.load(f)
        
    pred = xgb_model.predict(X)[0]
    return pred

pred_wh = predict_row(row)

req_per_month = 10000 * 24 * 30
monthly_energy_wh = pred_wh * req_per_month
monthly_energy_kwh = monthly_energy_wh / 1000.0
monthly_carbon_kg = monthly_energy_kwh * 0.708

gb_seconds = (row['memory_config_mb'] / 1024.0) * (row['aws_duration_ms'] / 1000.0)
compute_cost = gb_seconds * 0.001392
req_cost = 16.70 / 1000000
monthly_cost = req_per_month * (compute_cost + req_cost)

print(f"Predicted energy per invocation: {pred_wh:.6f} Wh")
print(f"Projected monthly carbon output: {monthly_carbon_kg:.3f} kg CO2")
print(f"Estimated monthly cost: Rs {monthly_cost:.2f}")

spike_requests = 10000 * 20 * 72
spike_energy_wh = pred_wh * spike_requests
spike_energy_kwh = spike_energy_wh / 1000.0
spike_carbon = spike_energy_kwh * 0.708
print(f"\nSpike (20x, 72h, {spike_requests} reqs):")
print(f"Projected total energy: {spike_energy_kwh:.3f} kWh")
print(f"Projected total carbon: {spike_carbon:.3f} kg CO2")
