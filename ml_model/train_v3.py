import os
import pickle
import time
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

print("="*60)
print("GREENLAMBDA MODEL RETRAINING (V3: COMBINED 175-FUNCTION DATASET)")
print("="*60)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')
NEW_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'new_ml_dataset.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'models')

# Load datasets
df_orig = pd.read_csv(ORIG_DATA_FILE)
df_new = pd.read_csv(NEW_DATA_FILE)

print(f"[*] Restored Original Dataset loaded: {len(df_orig)} rows")
print(f"[*] Expanded Dataset loaded: {len(df_new)} rows")

# Concat datasets
df = pd.concat([df_orig, df_new], ignore_index=True)
print(f"[*] Combined Dataset shape: {df.shape}")

# Recompute training target v3
# Formula: (10 + 0.2 * memory) * (duration / 3,600,000)
df['energy_target_wh_v3'] = (10.0 + 0.2 * df['memory_config_mb']) * (df['aws_duration_ms'] / 3600000.0)
print(f"[*] Target computed (v3). Mean: {df['energy_target_wh_v3'].mean():.6f} Wh")

# Align feature names
feat_path = os.path.join(MODELS_DIR, 'feature_names.pkl')
with open(feat_path, 'rb') as f:
    feature_names = pickle.load(f)
feature_names = [f for f in feature_names if f != 'calibration_ratio']
print(f"[*] Loaded feature list of length: {len(feature_names)}")

# One-hot encode categoricals
df_encoded = pd.get_dummies(df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)

# Align columns
for col in feature_names:
    if col not in df_encoded.columns:
        df_encoded[col] = 0.0

X = df_encoded[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0.0).astype(float)
y = df_encoded['energy_target_wh_v3']

print(f"[*] Feature matrix X shape: {X.shape}, Target y shape: {y.shape}")

# Train/Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Further split Train into Train/Validation for Neural Network/XGBoost early stopping (80/20 of train)
X_train_sub, X_val, y_train_sub, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Scaling preprocessors
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_sub_scaled = scaler.transform(X_train_sub)
X_val_scaled = scaler.transform(X_val)

# Save scaler for v3
with open(os.path.join(MODELS_DIR, 'scaler_v3.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

# K-Fold setup
kf = KFold(n_splits=5, shuffle=True, random_state=42)

print("\n--- Running 5-Fold Cross Validation ---")

# 1. XGBoost CV
print("Cross-validating XGBoost...")
xgb_cv_model = xgb.XGBRegressor(
    n_estimators=500,
    learning_rate=0.1,
    max_depth=10,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist'
)
xgb_cv = cross_validate(xgb_cv_model, X_train, y_train, cv=kf, scoring=['r2', 'neg_mean_absolute_error', 'neg_root_mean_squared_error'])

# 2. Random Forest CV
print("Cross-validating Random Forest...")
rf_cv_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
rf_cv = cross_validate(rf_cv_model, X_train, y_train, cv=kf, scoring=['r2', 'neg_mean_absolute_error', 'neg_root_mean_squared_error'])

# 3. Neural Network CV
print("Cross-validating Neural Network...")
nn_cv_model = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',
    batch_size=32,
    learning_rate_init=0.001,
    max_iter=100,
    early_stopping=True,
    validation_fraction=0.2,
    n_iter_no_change=10,
    random_state=42
)
nn_pipeline = Pipeline([('scaler', StandardScaler()), ('nn', nn_cv_model)])
nn_cv = cross_validate(nn_pipeline, X_train, y_train, cv=kf, scoring=['r2', 'neg_mean_absolute_error', 'neg_root_mean_squared_error'])

# Print CV results
print("\n=== 5-Fold CV Results ===")
print(f"XGBoost       - R2: {np.mean(xgb_cv['test_r2']):.4f}, MAE: {-np.mean(xgb_cv['test_neg_mean_absolute_error']):.6f} Wh, RMSE: {-np.mean(xgb_cv['test_neg_root_mean_squared_error']):.6f} Wh")
print(f"Random Forest - R2: {np.mean(rf_cv['test_r2']):.4f}, MAE: {-np.mean(rf_cv['test_neg_mean_absolute_error']):.6f} Wh, RMSE: {-np.mean(rf_cv['test_neg_root_mean_squared_error']):.6f} Wh")
print(f"Neural Net    - R2: {np.mean(nn_cv['test_r2']):.4f}, MAE: {-np.mean(nn_cv['test_neg_mean_absolute_error']):.6f} Wh, RMSE: {-np.mean(nn_cv['test_neg_root_mean_squared_error']):.6f} Wh")

print("\n--- Training Final Models ---")

# 1. XGBoost
print("Training final XGBoost model...")
xgb_model = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.1,
    max_depth=10,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    early_stopping_rounds=50,
    tree_method='hist'
)
start = time.time()
xgb_model.fit(X_train_sub, y_train_sub, eval_set=[(X_val, y_val)], verbose=False)
xgb_time = time.time() - start
xgb_preds = xgb_model.predict(X_test)
xgb_mae = mean_absolute_error(y_test, xgb_preds)
xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
xgb_r2 = r2_score(y_test, xgb_preds)

# 2. Random Forest
print("Training final Random Forest model...")
rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)
start = time.time()
rf_model.fit(X_train, y_train)
rf_time = time.time() - start
rf_preds = rf_model.predict(X_test)
rf_mae = mean_absolute_error(y_test, rf_preds)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
rf_r2 = r2_score(y_test, rf_preds)

# 3. Neural Network
print("Training final Neural Network model...")
nn_model = MLPRegressor(
    hidden_layer_sizes=(64, 32),
    activation='relu',
    solver='adam',
    batch_size=32,
    learning_rate_init=0.001,
    max_iter=100,
    early_stopping=True,
    validation_fraction=0.2,
    n_iter_no_change=10,
    random_state=42
)
start = time.time()
nn_model.fit(X_train_scaled, y_train)
nn_time = time.time() - start
nn_preds = nn_model.predict(X_test_scaled)
nn_mae = mean_absolute_error(y_test, nn_preds)
nn_rmse = np.sqrt(mean_squared_error(y_test, nn_preds))
nn_r2 = r2_score(y_test, nn_preds)

print("\n=== Final Test Set Results ===")
print(f"XGBoost       - R2: {xgb_r2:.4f}, MAE: {xgb_mae:.6f} Wh, RMSE: {xgb_rmse:.6f} Wh (Time: {xgb_time:.2f}s)")
print(f"Random Forest - R2: {rf_r2:.4f}, MAE: {rf_mae:.6f} Wh, RMSE: {rf_rmse:.6f} Wh (Time: {rf_time:.2f}s)")
print(f"Neural Net    - R2: {nn_r2:.4f}, MAE: {nn_mae:.6f} Wh, RMSE: {nn_rmse:.6f} Wh (Time: {nn_time:.2f}s)")

# Save new models
print("\nSaving V3 models to backend/models/...")
with open(os.path.join(MODELS_DIR, 'xgboost_model_v3.pkl'), 'wb') as f:
    pickle.dump(xgb_model, f)
with open(os.path.join(MODELS_DIR, 'random_forest_model_v3.pkl'), 'wb') as f:
    pickle.dump(rf_model, f)
with open(os.path.join(MODELS_DIR, 'neural_network_model_v3.pkl'), 'wb') as f:
    pickle.dump(nn_model, f)

print("[*] All V3 models saved successfully.")
print("="*60)
