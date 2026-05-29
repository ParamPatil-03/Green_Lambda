"""
Green Lambda LIME Explainer Module
==================================
This module integrates LIME (Local Interpretable Model-agnostic Explanations)
with the primary XGBoost, Random Forest, and Neural Network models to provide
local feature impact weights and global feature rankings.

Python 3.13.5 Compatibility Note:
---------------------------------
LIME depends on scikit-image, scipy, and numpy. If scikit-image fails to build, 
LIME can be installed using the '--no-deps' workaround:
    pip install lime --no-deps
    pip install numpy scipy scikit-learn
(lime's LimeTabularExplainer only requires these three core libraries, as
scikit-image is only needed for image explanations which are not used here).
"""

import os
import sys
import pandas as pd
import numpy as np

# Ensure the backend directory is accessible
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BACKEND_DIR)

import model_loader

# Initialize LIME with error handling for import issues
try:
    import lime
    import lime.lime_tabular
except ImportError as e:
    raise ImportError("LIME not installed. Run: pip install lime") from e

# Initialize global explainer variables
lime_explainer = None
feature_names = None
scaler = None
X_train_scaled = None
clean_df = None

# Paths
BASE_DIR = os.path.dirname(BACKEND_DIR)
DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')

def _initialize_lime():
    """
    Initializes the LimeTabularExplainer once at module startup using the full clean dataset.
    """
    global lime_explainer, feature_names, scaler, X_train_scaled, clean_df
    
    try:
        print("Initializing LIME Explainer module...")
        
        # 1. Fetch models, feature metadata, and scaler from model_loader
        loader = model_loader.get_loader()
        feature_names = loader.get_feature_names()
        scaler = loader.get_scaler()
        
        if feature_names is None or scaler is None:
            raise ValueError("Feature names or scaler not available from model_loader.")
            
        print(f"  - Retrieved {len(feature_names)} features and Standard Scaler")

        # 2. Load the baseline training dataset
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Baseline dataset file not found: {DATA_FILE}")
            
        clean_df = pd.read_csv(DATA_FILE)
        
        # 3. Perform One-Hot Encoding Alignment (same dummy-encoding as training)
        df_encoded = pd.get_dummies(clean_df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)
        
        # Ensure all training features are present in the dataframe
        for col in feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
                
        # Slice columns to match training order exactly and handle types
        X_all = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0).astype(float)
        
        # 4. Scale all rows using StandardScaler from model_loader (LIME requires scaled background for distribution)
        X_train_scaled = scaler.transform(X_all)
        print(f"  - Preprocessed LIME background dataset: {X_train_scaled.shape}")

        # 5. Initialize the LimeTabularExplainer
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_train_scaled,
            feature_names=feature_names,
            mode='regression',
            discretize_continuous=True,
            random_state=42
        )
        print("  - LimeTabularExplainer successfully initialized")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to initialize LIME Explainer: {e}")
        import traceback
        traceback.print_exc()

# Initialize immediately when module is imported
_initialize_lime()

def parse_lime_feature_name(feature_desc):
    """
    Extracts the clean feature name from a LIME condition string.
    Example: "0.20 < local_memory_mb <= 0.80" -> "local_memory_mb"
    Matches against the global feature_names list sorted by length descending to prevent substring collisions.
    """
    if not feature_names:
        return feature_desc
    sorted_features = sorted(feature_names, key=len, reverse=True)
    for f in sorted_features:
        if f in feature_desc:
            return f
    return feature_desc

def explain_with_lime(input_dict, model_name='xgboost'):
    """
    Generates local LIME explanations for a single prediction row.
    
    Parameters:
    - input_dict: Raw unscaled feature dictionary.
    - model_name: Target model name ('xgboost', 'random_forest', or 'neural_network').
    
    Returns:
    - dict: A structured JSON-serializable dictionary with weights and top 5 drivers.
    """
    global lime_explainer, feature_names, scaler
    
    try:
        loader = model_loader.get_loader()
        
        if model_name in ['neural_net', 'nn']: 
            model_name = 'neural_network'
        elif model_name == 'rf': 
            model_name = 'random_forest'
            
        model = loader.get_model(model_name)
        if model is None:
            model = loader.get_xgboost_model()
            
        if lime_explainer is None:
            raise RuntimeError("LIME explainer is not initialized.")
            
        # Convert input to DataFrame
        df_input = pd.DataFrame([input_dict])
        
        # Align features to training format
        df_aligned = model_loader.preprocess(df_input, for_model='xgboost')
        
        # Scale the row (LIME operates on scaled dataset)
        scaled_row = scaler.transform(df_aligned)[0]
        
        # Define prediction function for LIME
        def predict_fn(x_perturbed):
            # x_perturbed is in scaled space
            if model_name == 'neural_network':
                # Neural network model expects scaled inputs
                preds = model.predict(x_perturbed)
            else:
                # XGBoost and Random Forest expect unscaled inputs
                x_unscaled = scaler.inverse_transform(x_perturbed)
                df_unscaled = pd.DataFrame(x_unscaled, columns=feature_names)
                preds = model.predict(df_unscaled)
            return np.array(preds).flatten()
            
        # Run LIME local explanation
        exp = lime_explainer.explain_instance(
            data_row=scaled_row,
            predict_fn=predict_fn,
            num_features=len(feature_names),
            num_samples=1000
        )
        
        exp_list = exp.as_list()
        
        # Build dictionary of weights
        weights_dict = {}
        for desc, weight in exp_list:
            clean_name = parse_lime_feature_name(desc)
            weights_dict[clean_name] = float(weight)
            
        # Ordered weights matching feature_names
        lime_weights = [weights_dict.get(name, 0.0) for name in feature_names]
        
        # Extract top 5 contributors by absolute weight
        features_with_weight = []
        for name, weight in weights_dict.items():
            features_with_weight.append({
                "feature": name,
                "lime_weight": weight,
                "direction": "increases" if weight >= 0 else "decreases"
            })
            
        top_features = sorted(features_with_weight, key=lambda x: abs(x["lime_weight"]), reverse=True)[:5]
        
        # Get model predicted value for the input instance
        if model_name == 'neural_network':
            raw_pred = model.predict(scaler.transform(df_aligned))
        else:
            raw_pred = model.predict(df_aligned)
            
        predicted_val = float(raw_pred[0])
        
        # Extract intercept
        intercept = exp.intercept
        if isinstance(intercept, dict):
            intercept_val = float(list(intercept.values())[0])
        elif isinstance(intercept, (list, np.ndarray)):
            intercept_val = float(intercept[0])
        else:
            intercept_val = float(intercept)
            
        return {
            "feature_names": feature_names,
            "lime_weights": lime_weights,
            "top_features": top_features,
            "predicted_value": predicted_val,
            "intercept": intercept_val
        }
        
    except Exception as e:
        print(f"Error generating LIME explanation: {e}")
        import traceback
        traceback.print_exc()
        raise e

def get_lime_global_importance():
    """
    Computes global feature importance using LIME across a sample of 50 rows.
    WARNING: This takes ~50 seconds, only call when needed.
    """
    global clean_df, feature_names
    
    if clean_df is None or feature_names is None:
        raise RuntimeError("LIME explainer is not initialized.")
        
    print("[LIME] Computing global importance across 50 sample rows...")
    
    # Perform alignment on the full dataset (re-encoding for features alignment)
    df_encoded = pd.get_dummies(clean_df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
            
    # Sample 50 rows deterministically
    df_sample = df_encoded.sample(n=50, random_state=42)
    
    all_abs_weights = {name: [] for name in feature_names}
    
    for idx, row in df_sample.iterrows():
        # Convert row back to unencoded dict to match explain_with_lime inputs
        # Wait, explain_with_lime expects input_dict in raw format (unencoded), 
        # but it can also handle a flat feature dictionary with pre-aligned 34 features.
        # Since explain_with_lime performs model_loader.preprocess which can handle pre-encoded features,
        # we can pass the aligned dictionary directly!
        row_dict = row[feature_names].to_dict()
        try:
            explanation = explain_with_lime(row_dict, model_name='xgboost')
            # Extract weights and sum absolute values
            for name, weight in zip(explanation["feature_names"], explanation["lime_weights"]):
                all_abs_weights[name].append(abs(weight))
        except Exception as e:
            print(f"[LIME] Error explaining row {idx} for global importance: {e}")
            
    # Average the absolute weights
    importance_values = []
    ranked = []
    for name in feature_names:
        weights = all_abs_weights[name]
        mean_abs_weight = float(np.mean(weights)) if len(weights) > 0 else 0.0
        importance_values.append(mean_abs_weight)
        
    # Build ranked list sorted descending by importance
    for name, val in sorted(zip(feature_names, importance_values), key=lambda x: x[1], reverse=True):
        ranked.append({
            "feature": name,
            "importance": val
        })
        
    return {
        "feature_names": feature_names,
        "importance_values": importance_values,
        "ranked": ranked
    }
