"""
Green Lambda Model Loader Module
================================
This module implements a singleton pattern to load all trained ML models
and preprocessors once at startup.

Trained ML Features List — V3 (33 Features, calibration_ratio removed):
------------------------------------------------------------------------
1.  'memory_config_mb' (AWS Lambda Memory Allocation)
2.  'cold_start' (Cold Start Flag: 0 or 1)
3.  'lines_of_code' (Static Code Metric - LOC)
4.  'num_loops' (Static Code Metric - loop count)
5.  'num_conditionals' (Static Code Metric - conditional statements)
6.  'num_function_calls' (Static Code Metric - function calls)
7.  'cyclomatic_complexity' (Radon Cyclomatic Complexity)
8.  'max_nesting_depth' (Radon Code Nesting Depth)
9.  'local_duration_ms' (Dynamic Local Execution Time)
10. 'local_cpu_percent' (Dynamic Local CPU Utilization)
11. 'local_memory_mb' (Dynamic Local Memory Footprint)
12. 'aws_duration_ms' (AWS CloudWatch Duration metric)
13. 'aws_memory_used_mb' (AWS CloudWatch MaxMemoryUsed metric)
14. 'duration_ratio' (Ratio of aws_duration to local_duration)
15. 'memory_efficiency' (Ratio of aws_memory_used to memory_config)
16. 'function_name_array-operations' (One-hot encoded)
17. 'function_name_bubble-sort' (One-hot encoded)
18. 'function_name_csv-processor' (One-hot encoded)
19. 'function_name_data-transform' (One-hot encoded)
20. 'function_name_dict-builder' (One-hot encoded)
21. 'function_name_fibonacci' (One-hot encoded)
22. 'function_name_file-reader' (One-hot encoded)
23. 'function_name_json-parser' (One-hot encoded)
24. 'function_name_list-comprehension' (One-hot encoded)
25. 'function_name_matrix-multiply' (One-hot encoded)
26. 'function_name_prime-calculator' (One-hot encoded)
27. 'function_name_simple-encryption' (One-hot encoded)
28. 'function_name_string-concat' (One-hot encoded)
29. 'function_name_url-validator' (One-hot encoded)
30. 'function_type_io' (One-hot encoded)
31. 'function_type_memory' (One-hot encoded)
32. 'input_size_Medium' (One-hot encoded)
33. 'input_size_Small' (One-hot encoded)

Model Version: V3 (175 functions, 6132 records, combined dataset)
Target Formula: energy_wh = (10 + 0.2 * memory_config_mb) * (aws_duration_ms / 3600000)
"""

import os
import pickle
import pandas as pd
import numpy as np

class ModelLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelLoader, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.models = {}
        self.scaler = None
        self.feature_names = None
        self._load_all_artifacts()
        self._initialized = True

    def _load_all_artifacts(self):
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(backend_dir, 'models')

        print(f"Initializing ModelLoader: loading models from '{models_dir}'...")

        # 1. Load Feature Names
        feat_path = os.path.join(models_dir, 'feature_names.pkl')
        if os.path.exists(feat_path):
            with open(feat_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            print(f"  - Loaded feature names ({len(self.feature_names)} features)")
        else:
            raise FileNotFoundError(f"Feature names file not found: {feat_path}")

        # 2. Load Scaler (V3: scaler_v3.pkl fitted on 33-feature combined dataset)
        scaler_path = os.path.join(models_dir, 'scaler_v3.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            print("  - Loaded standard scaler (v3)")
        else:
            print("  - Warning: scaler_v3.pkl not found")

        # 3. Load Models (V3: trained on combined 175-function, 6132-record dataset)
        model_files = {
            'xgboost': 'xgboost_model_v3.pkl',
            'random_forest': 'random_forest_model_v3.pkl',
            'neural_network': 'neural_network_model_v3.pkl'
        }

        for model_key, filename in model_files.items():
            path = os.path.join(models_dir, filename)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    loaded_obj = pickle.load(f)
                
                # Check if it is a scikit-learn Pipeline and separate if requested
                if hasattr(loaded_obj, 'named_steps') and 'preprocessor' in loaded_obj.named_steps:
                    print(f"  - Extracted model '{model_key}' from scikit-learn Pipeline")
                    self.models[model_key] = loaded_obj.named_steps['model']
                    # Use pipeline preprocessor as scaler if scaler.pkl was missing
                    if self.scaler is None and 'preprocessor' in loaded_obj.named_steps:
                        self.scaler = loaded_obj.named_steps['preprocessor']
                else:
                    self.models[model_key] = loaded_obj
                
                print(f"  - Loaded {model_key} model")
            else:
                print(f"  - Warning: Model file {filename} not found")

    def get_model(self, model_name):
        """Returns the requested scikit-learn model wrapper."""
        return self.models.get(model_name)

    def get_xgboost_model(self):
        """Returns the loaded XGBoost scikit-learn model wrapper."""
        return self.models.get('xgboost')

    def get_xgboost_booster(self):
        """
        Returns the raw XGBoost Booster object.
        This is required for SHAP TreeExplainer, which needs the raw booster
        rather than the scikit-learn wrapper API.
        """
        xgb_model = self.models.get('xgboost')
        if xgb_model is not None:
            if hasattr(xgb_model, 'get_booster'):
                return xgb_model.get_booster()
            return xgb_model
        return None

    def get_random_forest_model(self):
        """Returns the loaded Random Forest model."""
        return self.models.get('random_forest')

    def get_neural_network_model(self):
        """Returns the loaded Neural Network model."""
        return self.models.get('neural_network')

    def get_scaler(self):
        """Returns the loaded Standard Scaler."""
        return self.scaler

    def get_feature_names(self):
        """Returns the exact list of feature names used during model training."""
        return self.feature_names

    def preprocess(self, X_single, for_model='xgboost'):
        """
        Preprocesses a DataFrame of raw features:
        1. Ensures the features are strictly in the correct feature name order.
        2. Converts features to numeric.
        3. If using Neural Network, applies Standard Scaling using the loaded scaler.
        
        Parameters:
        - X_single (pd.DataFrame): DataFrame of features.
        - for_model (str): Target model name ('xgboost', 'random_forest', or 'neural_network').
        
        Returns:
        - Preprocessed version (pd.DataFrame or np.ndarray) ready to be fed into the model.
        """
        # Ensure column order aligns exactly with training features
        if self.feature_names:
            # Add missing columns
            for col in self.feature_names:
                if col not in X_single.columns:
                    X_single[col] = 0
            # Reorder
            X_single = X_single[self.feature_names]

        # Force every column to numeric
        X_single = X_single.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Apply scaling if Neural Network is requested
        if for_model in ['neural_network', 'neural_net', 'nn']:
            if self.scaler:
                return self.scaler.transform(X_single)
            else:
                print("Warning: scaling requested for NN but scaler is not available")
        
        return X_single

# Global Singleton instance
_loader_instance = None

def get_loader():
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = ModelLoader()
    return _loader_instance

# Global helper functions for convenience
def get_xgboost_model():
    return get_loader().get_xgboost_model()

def get_xgboost_booster():
    return get_loader().get_xgboost_booster()

def get_random_forest_model():
    return get_loader().get_random_forest_model()

def get_neural_network_model():
    return get_loader().get_neural_network_model()

def get_scaler():
    return get_loader().get_scaler()

def get_feature_names():
    return get_loader().get_feature_names()

def preprocess(X_single, for_model='xgboost'):
    return get_loader().preprocess(X_single, for_model=for_model)
