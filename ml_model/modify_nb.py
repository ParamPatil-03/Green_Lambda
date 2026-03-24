import nbformat as nbf

nb_file = r'c:\Users\PARAM\Desktop\mini project\ml_model\model.ipynb'

with open(nb_file, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

cell_split = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("DATA PREPROCESSING (TRAIN/TEST SPLIT & SCALING)")
print("="*60)

import os
import pickle

# Target and inputs
target = 'energy_target_wh'

# Input features (16)
features = [
    'function_name', 'function_type', 'input_size', 'memory_config_mb', 
    'cold_start', 'lines_of_code', 'num_loops', 'num_conditionals', 
    'num_function_calls', 'cyclomatic_complexity', 'max_nesting_depth', 
    'local_duration_ms', 'local_cpu_percent', 'local_memory_mb', 
    'aws_duration_ms', 'aws_memory_used_mb', 'duration_ratio', 
    'memory_efficiency', 'calibration_ratio'
]

# We need to one-hot encode categorical features: function_name, function_type, input_size
df_encoded = pd.get_dummies(df, columns=['function_name', 'function_type', 'input_size'], drop_first=True)

# All columns except target and non-input derived features that leak the target
# From the guide, there are 16 input features + one-hot encodings.
drop_cols = ['energy_target_wh', 'local_energy_wh', 'aws_energy_estimate_wh', 'aws_cold_start']
X = df_encoded.drop(columns=drop_cols)
y = df_encoded[target]

# Train / Test split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Further split Train into Train/Validation for Neural Network/XGBoost early stopping (80/20 of train)
X_train_sub, X_val, y_train_sub, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Scaling for Neural Network
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_sub_scaled = scaler.transform(X_train_sub)
X_val_scaled = scaler.transform(X_val)

feature_names = list(X.columns)

print(f"✓ Data split successfully: {len(X_train)} train samples, {len(X_test)} test samples")
print(f"✓ Neural Network features scaled")
print(f"✓ Prepared {len(feature_names)} features after encoding")""")

cell_xgb = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("TRAINING MODEL 1: XGBOOST (PRIMARY)")
print("="*60)

start_time = time.time()

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

# Train XGBoost
xgb_model.fit(
    X_train_sub, y_train_sub,
    eval_set=[(X_val, y_val)],
    verbose=False
)

xgb_time = time.time() - start_time

# Predict on test set
xgb_preds = xgb_model.predict(X_test)

# Metrics
xgb_mae = mean_absolute_error(y_test, xgb_preds)
xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))
xgb_r2 = r2_score(y_test, xgb_preds)

print(f"✓ XGBoost Training Complete in {xgb_time:.2f} seconds")
print(f"  MAE:  {xgb_mae:.4f} Wh")
print(f"  RMSE: {xgb_rmse:.4f} Wh")
print(f"  R²:   {xgb_r2:.4f}")""")

cell_rf = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("TRAINING MODEL 2: RANDOM FOREST (BACKUP)")
print("="*60)

start_time = time.time()

rf_model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_time = time.time() - start_time

# Predict
rf_preds = rf_model.predict(X_test)

# Metrics
rf_mae = mean_absolute_error(y_test, rf_preds)
rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
rf_r2 = r2_score(y_test, rf_preds)

print(f"✓ Random Forest Training Complete in {rf_time:.2f} seconds")
print(f"  MAE:  {rf_mae:.4f} Wh")
print(f"  RMSE: {rf_rmse:.4f} Wh")
print(f"  R²:   {rf_r2:.4f}")""")

cell_nn = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("TRAINING MODEL 3: NEURAL NETWORK (EXPERIMENTAL)")
print("="*60)

start_time = time.time()

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

# Train on SCALED data
nn_model.fit(X_train_scaled, y_train)

nn_time = time.time() - start_time

# Predict
nn_preds = nn_model.predict(X_test_scaled)

# Metrics
nn_mae = mean_absolute_error(y_test, nn_preds)
nn_rmse = np.sqrt(mean_squared_error(y_test, nn_preds))
nn_r2 = r2_score(y_test, nn_preds)

print(f"✓ Neural Network Training Complete in {nn_time:.2f} seconds")
print(f"  MAE:  {nn_mae:.4f} Wh")
print(f"  RMSE: {nn_rmse:.4f} Wh")
print(f"  R²:   {nn_r2:.4f}")""")

cell_comparison = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("MODEL EVALUATION & COMPARISON")
print("="*60)

# Create comparison dataframe
results_df = pd.DataFrame({
    'Model': ['XGBoost', 'Random Forest', 'Neural Network'],
    'MAE (Wh)': [xgb_mae, rf_mae, nn_mae],
    'RMSE' : [xgb_rmse, rf_rmse, nn_rmse],
    'R² Score': [xgb_r2, rf_r2, nn_r2],
    'Training Time (s)': [xgb_time, rf_time, nn_time]
})

print("\\nModel Performance Complete Comparison:")
print(results_df.round(4).to_string(index=False))

# Plot Comparison
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

bars = ax[0].bar(results_df['Model'], results_df['R² Score'], color=['#3498db', '#2ecc71', '#9b59b6'])
ax[0].set_ylim(0.8, 1.0)
ax[0].set_title('R² Score Comparison (Higher is better)')
ax[0].set_ylabel('R² Score')
for bar in bars:
    yval = bar.get_height()
    ax[0].text(bar.get_x() + bar.get_width()/2, yval + 0.005, f"{yval:.4f}", ha='center', va='bottom')

bars2 = ax[1].bar(results_df['Model'], results_df['MAE (Wh)'], color=['#e74c3c', '#e67e22', '#f1c40f'])
ax[1].set_title('Mean Absolute Error (Lower is better)')
ax[1].set_ylabel('MAE (Wh)')
for bar in bars2:
    yval = bar.get_height()
    ax[1].text(bar.get_x() + bar.get_width()/2, yval + 0.002, f"{yval:.4f}", ha='center', va='bottom')

plt.tight_layout()
plt.show()""")

cell_feature_importance = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("FEATURE IMPORTANCE (XGBOOST)")
print("="*60)

# Get feature importance from XGBoost
importance = xgb_model.feature_importances_
feat_imp = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importance
}).sort_values('Importance', ascending=False).reset_index(drop=True)

feat_imp['Rank'] = feat_imp.index + 1

print("\\nTop 10 Most Important Features:")
print(feat_imp.head(10).to_string(index=False))

# Plot Feature Importance
plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feat_imp.head(15), palette='viridis')
plt.title('Top 15 Feature Importances (XGBoost)', fontsize=14, fontweight='bold')
plt.xlabel('Relative Importance')
plt.tight_layout()
plt.show()""")

cell_saving = nbf.v4.new_code_cell("""print("\\n" + "="*60)
print("SAVING MODELS TO STORAGE")
print("="*60)

import os

models_dir = '../backend/models'
results_dir = '../backend/results'
os.makedirs(models_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

# Save XGBoost
with open(os.path.join(models_dir, 'xgboost_model.pkl'), 'wb') as f:
    pickle.dump(xgb_model, f)

# Save Random Forest
with open(os.path.join(models_dir, 'random_forest_model.pkl'), 'wb') as f:
    pickle.dump(rf_model, f)

# Save Neural Network
with open(os.path.join(models_dir, 'neural_network_model.pkl'), 'wb') as f:
    pickle.dump(nn_model, f)

# Save Scaler
with open(os.path.join(models_dir, 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)

# Save Feature Names
with open(os.path.join(models_dir, 'feature_names.pkl'), 'wb') as f:
    pickle.dump(feature_names, f)

# Save results CSV
results_df.to_csv(os.path.join(results_dir, 'model_comparison.csv'), index=False)
feat_imp.to_csv(os.path.join(results_dir, 'feature_importance.csv'), index=False)

def get_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024)

print(f"✓ Models successfully saved in {os.path.abspath(models_dir)}")
print(f"  - XGBoost Checkpoint: {get_size_mb(os.path.join(models_dir, 'xgboost_model.pkl')):.2f} MB")
print(f"  - Random Forest Checkpoint: {get_size_mb(os.path.join(models_dir, 'random_forest_model.pkl')):.2f} MB")
print(f"  - Neural Network Checkpoint: {get_size_mb(os.path.join(models_dir, 'neural_network_model.pkl')):.2f} MB")
print(f"  - Scaler & Feature metadata saved.")
print(f"✓ Results successfully saved in {os.path.abspath(results_dir)}")""")

nb['cells'].extend([cell_split, cell_xgb, cell_rf, cell_nn, cell_comparison, cell_feature_importance, cell_saving])

with open(nb_file, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
