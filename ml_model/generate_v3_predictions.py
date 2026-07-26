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

# Function to extract features, encode, and predict
def predict_row(row):
    # Load feature names
    feat_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
    with open(feat_path, 'rb') as f:
        feature_names = pickle.load(f)
    feature_names = [f for f in feature_names if f != 'calibration_ratio']
    
    # Create single row df
    row_df = pd.DataFrame([row])
    
    # One-hot encode categoricals
    df_encoded = pd.get_dummies(row_df, columns=['function_name', 'function_type', 'input_size'], drop_first=False)
    
    # Align columns
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0.0
            
    X = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)
    
    # Predict
    with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'rb') as f:
        xgb_model = pickle.load(f)
        
    pred = xgb_model.predict(X)[0]
    return pred

print("="*50)
print("3. dict-builder at 1024MB")
dict_row = df[(df['function_name'] == 'dict-builder') & (df['memory_config_mb'] == 1024)].iloc[0]
print(f"Original duration: {dict_row['aws_duration_ms']} ms")
pred_wh = predict_row(dict_row)

req_per_month = 10000 * 24 * 30
monthly_energy_wh = pred_wh * req_per_month
monthly_energy_kwh = monthly_energy_wh / 1000.0
monthly_carbon_kg = monthly_energy_kwh * 0.708

gb_seconds = (dict_row['memory_config_mb'] / 1024.0) * (dict_row['aws_duration_ms'] / 1000.0)
compute_cost = gb_seconds * 0.001392
req_cost = 16.70 / 1000000
monthly_cost = req_per_month * (compute_cost + req_cost)

print(f"Predicted energy per invocation: {pred_wh:.6f} Wh")
print(f"Projected monthly carbon output: {monthly_carbon_kg:.3f} kg CO2")
print(f"Estimated monthly cost: Rs {monthly_cost:.2f}")

# Spike simulator: 20x multiplier over 72 hours
# 72 hours at 10,000 req/hr * 20 = 200,000 req/hr * 72 = 14,400,000 requests
spike_requests = 10000 * 20 * 72
spike_energy_wh = pred_wh * spike_requests
spike_energy_kwh = spike_energy_wh / 1000.0
spike_carbon = spike_energy_kwh * 0.708
print(f"\nSpike (20x, 72h, {spike_requests} reqs):")
print(f"Projected total energy: {spike_energy_kwh:.3f} kWh")
print(f"Projected total carbon: {spike_carbon:.3f} kg CO2")

print("\n"+"="*50)
print("4. bubble-sort at 512MB")
bubble_row = df[(df['function_name'] == 'bubble-sort') & (df['memory_config_mb'] == 512)].iloc[0]
print(f"Original duration: {bubble_row['aws_duration_ms']} ms")
bubble_pred_wh = predict_row(bubble_row)
theoretical = (10.0 + 0.2 * 512) * (bubble_row['aws_duration_ms'] / 3600000.0)

print(f"Theoretical formula value: {theoretical:.6f} Wh")
print(f"Model predicted energy per invocation: {bubble_pred_wh:.6f} Wh")
print(f"Difference: {abs(theoretical - bubble_pred_wh):.6f} Wh")
print("="*50)
