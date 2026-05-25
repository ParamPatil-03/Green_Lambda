"""
Green Lambda SHAP Explainer Module
==================================
This module integrates SHAP (SHapley Additive exPlanations) with the primary
XGBoost prediction model to provide transparent, human-readable explanations
for energy consumption forecasts in physical units (mWh).

It uses Option B: passing the full XGBRegressor scikit-learn wrapper object
to SHAP TreeExplainer, so the resulting SHAP values align directly with the
prediction scale (mWh), avoiding raw margin space.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
import shap

# Ensure the backend directory is accessible
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

import model_loader

# Initialize global explainers
xgb_explainer = None
rf_explainer = None
nn_explainer = None
feature_names = None
X_background = None
global_importance_data = None

# Paths
BASE_DIR = os.path.dirname(BACKEND_DIR)
DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')

def _initialize_shap():
    """
    Initializes all three SHAP explainers (XGBoost TreeExplainer, Random Forest TreeExplainer,
    and Neural Network KernelExplainer) once at module startup.
    """
    global xgb_explainer, rf_explainer, nn_explainer, feature_names, X_background, global_importance_data
    
    try:
        print("Initializing SHAP Explainer module...")
        
        # 1. Fetch models and feature metadata from model_loader
        loader = model_loader.get_loader()
        xgb_model = loader.get_xgboost_model()
        rf_model = loader.get_random_forest_model()
        nn_model = loader.get_neural_network_model()
        feature_names = loader.get_feature_names()
        
        if any(m is None for m in [xgb_model, rf_model, nn_model]) or feature_names is None:
            raise ValueError("Required models or feature names list not available from model_loader.")
            
        print(f"  - Retrieved models and {len(feature_names)} features metadata")

        # 2. Load the baseline training dataset
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Baseline dataset file not found: {DATA_FILE}")
            
        df = pd.read_csv(DATA_FILE)
        
        # 3. Perform One-Hot Encoding Alignment (same dummy-encoding as training)
        df_encoded = pd.get_dummies(df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)
        
        # Ensure all training features are present in the dataframe
        for col in feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
                
        # Slice columns to match training order exactly and handle types
        X_all = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)
        
        # 4. Extract exactly 100 rows as the background baseline dataset
        # We use random_state=42 for deterministic baseline comparisons
        X_background = X_all.sample(n=100, random_state=42)
        print(f"  - Preprocessed background baseline dataset: {X_background.shape}")

        # 5. Initialize the SHAP Explainers
        print("  - Initializing XGBoost TreeExplainer...")
        xgb_explainer = shap.TreeExplainer(xgb_model, X_background)
        
        print("  - Initializing Random Forest TreeExplainer...")
        rf_explainer = shap.TreeExplainer(rf_model, X_background)
        
        print("  - Initializing Neural Network KernelExplainer...")
        def nn_predict(X):
            X_scaled = loader.preprocess(pd.DataFrame(X, columns=feature_names), for_model='neural_network')
            return nn_model.predict(X_scaled)
            
        nn_background = shap.kmeans(X_background, 5)
        nn_explainer = shap.KernelExplainer(nn_predict, nn_background)
        print("  - SHAP Explainers successfully initialized")

        # 6. Pre-calculate and cache the Global Feature Importance using XGBoost as reference
        print("  - Computing and caching global SHAP feature importances...")
        shap_values_global = xgb_explainer.shap_values(X_background)
        
        # Handle SHAP multi-output list responses robustly (e.g. if wrapper behaves as multi-class)
        if isinstance(shap_values_global, list):
            shap_matrix = shap_values_global[0]
        else:
            shap_matrix = shap_values_global
            
        # Compute the mean absolute SHAP value per feature
        mean_abs_shap = np.mean(np.abs(shap_matrix), axis=0)
        
        importance_list = [float(val) for val in mean_abs_shap]
        
        # Create a ranked features list sorted descending by importance
        ranked_features = []
        for name, val in sorted(zip(feature_names, importance_list), key=lambda x: x[1], reverse=True):
            ranked_features.append({
                "feature": name,
                "importance": float(val)
            })
            
        global_importance_data = {
            "feature_names": feature_names,
            "importance_values": importance_list,
            "ranked": ranked_features
        }
        print("  - Global SHAP feature importances successfully cached")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize SHAP Explainer: {e}")
        import traceback
        traceback.print_exc()

# Initialize immediately when the module is imported
_initialize_shap()

def explain_prediction(raw_features, model_name='xgboost'):
    """
    Generates local SHAP explanations for a single prediction row using the requested model.
    
    Parameters:
    - raw_features: Can be a dict, pandas Series, or a pandas DataFrame.
                    Accepts either unencoded raw variables or pre-aligned 34-feature representations.
    - model_name: Target model name ('xgboost', 'random_forest', or 'neural_network').
                    
    Returns:
    - dict: A structured, fully JSON-serializable dictionary
    """
    global xgb_explainer, rf_explainer, nn_explainer
    
    if model_name in ['neural_net', 'nn']: model_name = 'neural_network'
    elif model_name == 'rf': model_name = 'random_forest'
    
    explainer = xgb_explainer
    if model_name == 'random_forest':
        explainer = rf_explainer
    elif model_name == 'neural_network':
        explainer = nn_explainer
        
    if explainer is None:
        raise RuntimeError(f"SHAP Explainer for model '{model_name}' has not been initialized.")
        
    # Convert input to DataFrame if it's a dict or pandas Series
    if isinstance(raw_features, dict):
        df_input = pd.DataFrame([raw_features])
    elif isinstance(raw_features, pd.Series):
        df_input = pd.DataFrame([raw_features])
    elif isinstance(raw_features, pd.DataFrame):
        df_input = raw_features.copy()
    else:
        raise TypeError("Input must be a dictionary, pandas Series, or DataFrame.")

    # 1. Align features to the exact 34 training columns in order
    df_preprocessed = model_loader.preprocess(df_input, for_model='xgboost')

    # 2. Run SHAP values calculation
    shap_results = explainer.shap_values(df_preprocessed)
    
    # Handle multi-output lists or multi-dimensional arrays robustly
    if isinstance(shap_results, list):
        shap_arr = shap_results[0]
    else:
        shap_arr = shap_results
        
    # Flatten single row matrix (1x34) to a 1D array (34,)
    if len(shap_arr.shape) > 1 and shap_arr.shape[0] == 1:
        shap_arr = shap_arr[0]
        
    # Convert elements to standard Python float to ensure JSON serializability
    shap_values_list = [float(v) for v in shap_arr]
    
    # Calculate baseline and final predicted values
    if model_name == 'neural_network':
        base_val = explainer.expected_value
        if isinstance(base_val, (list, np.ndarray)):
            base_val = float(base_val[0])
        else:
            base_val = float(base_val)
    else:
        base_val = float(explainer.expected_value)
        
    predicted_val = base_val + float(np.sum(shap_arr))

    # 3. Format Local Explanations and extract Top 5 contributors
    features_with_shap = []
    for name, val in zip(feature_names, shap_values_list):
        features_with_shap.append({
            "feature": name,
            "shap_value": val,
            "direction": "increases" if val >= 0 else "decreases"
        })

    # Sort descending by absolute impact
    top_features = sorted(features_with_shap, key=lambda x: abs(x["shap_value"]), reverse=True)[:5]

    return {
        "feature_names": feature_names,
        "shap_values": shap_values_list,
        "base_value": base_val,
        "predicted_value": predicted_val,
        "top_features": top_features
    }

def get_global_importance():
    """
    Returns the pre-calculated, cached global feature importance metrics.
    
    Returns:
    - dict: A structured, JSON-serializable dictionary of ranked feature importances.
    """
    if global_importance_data is None:
        raise RuntimeError("SHAP Explainer has not been initialized.")
    return global_importance_data
