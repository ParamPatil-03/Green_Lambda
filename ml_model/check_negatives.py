import os
import pickle
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, '..', 'backend', 'models')
DATA_FILE1 = os.path.join(BASE_DIR, 'final_ml_dataset_clean.csv')
DATA_FILE2 = os.path.join(BASE_DIR, 'new_ml_dataset.csv')

def run_analysis():
    # Load dataset
    df1 = pd.read_csv(DATA_FILE1)
    df2 = pd.read_csv(DATA_FILE2)
    df = pd.concat([df1, df2], ignore_index=True)
    
    with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'rb') as f:
        model = pickle.load(f)
        
    with open(os.path.join(MODELS_DIR, 'feature_names.pkl'), 'rb') as f:
        feature_names = pickle.load(f)
        
    feature_names = [f for f in feature_names if f != 'calibration_ratio']
    
    # We will test using the aggregated approach exactly like the backend does.
    fn_features = df.groupby('function_name').mean(numeric_only=True).reset_index()
    df_cat = df.groupby('function_name')[['function_type', 'input_size']].agg(lambda x: x.mode()[0]).reset_index()
    fn_lookup = pd.merge(fn_features, df_cat, on='function_name')
    
    negatives = []
    
    print(f"Total unique functions to test: {len(fn_lookup)}")
    
    for _, row in fn_lookup.iterrows():
        # Prepare features for this row
        row_df = pd.DataFrame([row])
        df_encoded = pd.get_dummies(row_df, columns=['function_name', 'function_type', 'input_size'])
        
        for col in feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0.0
                
        X = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)
        
        pred = float(model.predict(X)[0])
        
        if pred < 0:
            negatives.append({
                'name': row['function_name'],
                'type': row['function_type'],
                'memory_mb': row['memory_config_mb'],
                'duration_ms': row['aws_duration_ms'],
                'prediction': pred
            })
            
    print(f"\nFound {len(negatives)} negative predictions.")
    if negatives:
        print("\nNegative predictions:")
        for n in negatives:
            print(f"- {n['name']} ({n['type']}): {n['prediction']:.6f} Wh | Memory: {n['memory_mb']} MB | Duration: {n['duration_ms']:.2f} ms")
            
if __name__ == "__main__":
    run_analysis()
