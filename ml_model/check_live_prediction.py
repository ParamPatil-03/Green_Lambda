import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')
NEW_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'new_ml_dataset.csv')

df_orig = pd.read_csv(ORIG_DATA_FILE)
df_new = pd.read_csv(NEW_DATA_FILE)
df = pd.concat([df_orig, df_new], ignore_index=True)

target_func = 'etl-transform-10'
func_rows = df[df['function_name'] == target_func]
row_series = func_rows.iloc[0].copy()

# Override with Live Values
row_series['aws_duration_ms'] = 3.656888888888889
row_series['lines_of_code'] = 39.0
row_series['cyclomatic_complexity'] = 7.0

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
        
    return xgb_model.predict(X)[0]

pred = predict_row(row_series)
print(f"Energy Prediction with Live Overrides: {pred:.6f}")
