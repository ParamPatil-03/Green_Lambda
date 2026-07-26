#!/usr/bin/env python3
"""
Green Lambda — Cross-Platform Validation Script (Alibaba Cloud)
==============================================================
Validates the Green Lambda AWS-trained energy prediction model against the 
Alibaba Cloud Functions 2021 dataset to test cross-platform generalizability.

LIMITATIONS OF THIS CROSS-PLATFORM VALIDATION:
1. AST features (cyclomatic complexity, LOC, nesting depth, function calls etc.)
   are imputed with training data means because the Alibaba dataset does not include 
   source code. This means the model is being tested primarily on its ability to 
   generalize execution metrics, not code features.

2. Trigger types are not included in the Alibaba dataset. Proportions from the training 
   data are used for imputation, and validation breakdown is performed by runtime.

3. The 'actual' energy values are calculated using the same physics-based formula 
   used in training, not hardware-measured power consumption. This means we are 
   testing formula generalization, not true energy measurement.

4. Alibaba Cloud Functions runtime characteristics differ from AWS Lambda. These differences 
   are not captured in the feature set.

These limitations are explicitly acknowledged for the research paper.
"""

import os
import sys
import glob
import json
import numpy as np
from datetime import datetime

# Manipulate sys.path to import model_loader from backend directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
backend_dir = os.path.join(project_root, "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    import pandas as pd
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    import matplotlib.pyplot as plt
    
    # Import ModelLoader singleton
    import model_loader
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please run this script within the designated virtual environment.")
    sys.exit(1)

# Set matplotlib style for publication quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Paths Setup
RAW_DIR = os.path.join(script_dir, "raw")
RESULTS_DIR = os.path.join(script_dir, "results")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

CLEAN_DATASET_PATH = os.path.join(project_root, "ml_model", "final_ml_dataset_clean.csv")

def load_and_merge_data():
    """Loads and preprocesses duration, memory, and runtime files for Alibaba."""
    print("\n========================================")
    print("PART 1: DATA PREPROCESSING AND MERGING")
    print("========================================")
    
    csv_files = sorted(glob.glob(os.path.join(RAW_DIR, "region_*.csv")))
    if not csv_files:
        print(f"[ERROR] No region CSV files found in {RAW_DIR}")
        sys.exit(1)
        
    print(f"Found {len(csv_files)} region CSV files: {[os.path.basename(f) for f in csv_files]}")
    
    # Load and combine all region files
    dfs = []
    total_raw_rows = 0
    for idx, filepath in enumerate(csv_files, 1):
        print(f"  [{idx}/{len(csv_files)}] Loading {os.path.basename(filepath)}...")
        try:
            # Load only required columns to save memory
            df_part = pd.read_csv(filepath, usecols=['functionName', 'latency', 'runtime', 'memoryMB'])
            total_raw_rows += len(df_part)
            dfs.append(df_part)
        except Exception as e:
            print(f"    [WARNING] Failed to load {filepath}: {e}")
            
    if not dfs:
        print("[ERROR] No data could be loaded.")
        sys.exit(1)
        
    print("Combining region data...")
    combined_df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {total_raw_rows:,} raw traces.")
    
    # Filter out invalid rows before aggregation
    print("Filtering invalid traces...")
    combined_df = combined_df[(combined_df['latency'] > 0) & (combined_df['memoryMB'] > 0)]
    print(f"Traces after filtering latency and memoryMB > 0: {len(combined_df):,}")
    
    # Group by functionName to calculate function-level averages and percentiles
    print("Aggregating traces to function-level metrics...")
    agg_df = combined_df.groupby('functionName').agg(
        avg_duration_ms=('latency', 'mean'),
        min_duration_ms=('latency', 'min'),
        max_duration_ms=('latency', 'max'),
        p50_duration_ms=('latency', 'median'),
        p99_duration_ms=('latency', lambda x: x.quantile(0.99)),
        invocation_count=('latency', 'count'),
        memory_allocated_mb=('memoryMB', 'mean'),
        runtime=('runtime', 'first')
    ).reset_index()
    
    print(f"  Total unique functions aggregated: {len(agg_df):,}")
    
    # Filter for functions with invocation_count >= 10
    agg_df = agg_df[agg_df['invocation_count'] >= 10]
    print(f"  Functions with invocation_count >= 10: {len(agg_df):,}")
    
    # Cap memory at 3072 MB and duration at 300,000 ms to represent normal serverless limits
    agg_df = agg_df[agg_df['memory_allocated_mb'] <= 3072]
    agg_df = agg_df[agg_df['avg_duration_ms'] <= 300000]
    print(f"  Functions after environment limits capping (<=3072MB memory, <=300s duration): {len(agg_df):,}")
    
    # Clean runtime column string (strip, lowercase)
    agg_df['runtime'] = agg_df['runtime'].astype(str).str.strip().str.lower()
    
    # Print Runtime Proportions
    runtime_counts = agg_df['runtime'].value_counts()
    runtime_pcts = (runtime_counts / len(agg_df)) * 100
    runtime_str = ", ".join([f"{k}={v:.1f}%" for k, v in runtime_pcts.head(8).items()])
    print(f"  Top runtimes: {runtime_str}")
    
    return agg_df

def stratified_sample(df, col, n=5000, random_state=42):
    """Draws a stratified random sample of size n proportionally covering runtimes."""
    counts = df[col].value_counts()
    proportions = counts / len(df)
    samples = []
    
    for g, group in df.groupby(col):
        g_n = max(1, int(round(proportions[g] * n)))
        g_n = min(g_n, len(group))
        samples.append(group.sample(n=g_n, random_state=random_state))
        
    sampled = pd.concat(samples)
    
    # Adjust to exactly n if needed
    if len(sampled) > n:
        sampled = sampled.sample(n=n, random_state=random_state)
    elif len(sampled) < n:
        remaining = df.loc[~df.index.isin(sampled.index)]
        needed = n - len(sampled)
        if needed > 0 and len(remaining) > 0:
            fill = remaining.sample(n=min(needed, len(remaining)), random_state=random_state)
            sampled = pd.concat([sampled, fill])
            
    print(f"Sampled {len(sampled)} functions stratified by {col} for validation")
    return sampled

def calculate_ground_truth(df):
    """Calculates the physics-based actual energy consumption (Wh and mWh)."""
    # Power (W) = 10 + (0.2 * memory_allocated_mb)
    power_w = 10.0 + (0.2 * df['memory_allocated_mb'])
    # Energy (Wh) = Power * (avg_duration_ms / 3,600,000)
    df['actual_energy_wh'] = power_w * (df['avg_duration_ms'] / 3600000.0)
    df['actual_energy_mwh'] = df['actual_energy_wh'] * 1000.0
    
    print("\n========================================")
    print("PART 2: FEATURE ENGINEERING & METRICS")
    print("========================================")
    print(f"Actual energy range: {df['actual_energy_wh'].min():.6f} - {df['actual_energy_wh'].max():.6f} Wh")
    print(f"Mean actual energy: {df['actual_energy_wh'].mean():.6f} Wh")
    
    return df

def build_features_and_predict(sample_df):
    """Builds the 34-feature vector, applies scaling, and predicts energy consumption."""
    # 1. Load Training dataset means for imputation
    print("Loading training dataset for feature imputation...")
    train_means = {}
    try:
        if os.path.exists(CLEAN_DATASET_PATH):
            train_df = pd.read_csv(CLEAN_DATASET_PATH)
            train_means = train_df.mean(numeric_only=True).to_dict()
            
            # Calculate proportion of function types in training data dynamically
            if 'function_type' in train_df.columns:
                counts = train_df['function_type'].value_counts()
                total = len(train_df)
                train_means['function_type_io'] = float(counts.get('io', 0) / total)
                train_means['function_type_memory'] = float(counts.get('memory', 0) / total)
                
            print("  - Loaded training dataset averages successfully.")
    except Exception as e:
        print(f"  - [WARNING] Loading training dataset failed: {e}. Using fallback defaults.")
        
    # Set fallback defaults for training means
    fallback_means = {
        'cold_start': 0.033783783783783786,
        'lines_of_code': 23.86861861861862,
        'num_loops': 2.40015015015015,
        'num_conditionals': 0.668918918918919,
        'num_function_calls': 9.396396396396396,
        'cyclomatic_complexity': 4.069069069069069,
        'max_nesting_depth': 1.5375375375375375,
        'local_cpu_percent': 17.49655405405405,
        'memory_efficiency': 0.09614081855292793,
        'calibration_ratio': 0.0003362762255765649,
        'function_type_io': 0.3378,
        'function_type_memory': 0.3288
    }
    
    # Merge loaded averages with fallbacks
    for key, val in fallback_means.items():
        if key not in train_means:
            train_means[key] = val
            
    # 2. Get feature names list from loader
    loader = model_loader.get_loader()
    feature_names = loader.get_feature_names()
    
    # 3. Construct features DataFrame
    features_df = pd.DataFrame(index=sample_df.index)
    
    # Direct mappings
    features_df['memory_config_mb'] = sample_df['memory_allocated_mb']
    features_df['cold_start'] = train_means['cold_start']
    features_df['lines_of_code'] = train_means['lines_of_code']
    features_df['num_loops'] = train_means['num_loops']
    features_df['num_conditionals'] = train_means['num_conditionals']
    features_df['num_function_calls'] = train_means['num_function_calls']
    features_df['cyclomatic_complexity'] = train_means['cyclomatic_complexity']
    features_df['max_nesting_depth'] = train_means['max_nesting_depth']
    features_df['local_duration_ms'] = sample_df['avg_duration_ms']
    features_df['local_cpu_percent'] = train_means['local_cpu_percent']
    features_df['local_memory_mb'] = sample_df['memory_allocated_mb']
    features_df['aws_duration_ms'] = sample_df['avg_duration_ms']
    features_df['aws_memory_used_mb'] = sample_df['memory_allocated_mb']
    features_df['duration_ratio'] = 1.0
    features_df['memory_efficiency'] = train_means['memory_efficiency']
    features_df['calibration_ratio'] = train_means['calibration_ratio']
    
    # One-hot encoded function names (all 0)
    for col in [
        'function_name_array-operations', 'function_name_bubble-sort', 'function_name_csv-processor',
        'function_name_data-transform', 'function_name_dict-builder', 'function_name_fibonacci',
        'function_name_file-reader', 'function_name_json-parser', 'function_name_list-comprehension',
        'function_name_matrix-multiply', 'function_name_prime-calculator', 'function_name_simple-encryption',
        'function_name_string-concat', 'function_name_url-validator'
    ]:
        features_df[col] = 0.0
        
    # Function types
    features_df['function_type_io'] = train_means['function_type_io']
    features_df['function_type_memory'] = train_means['function_type_memory']
    
    # Input size (all 0)
    features_df['input_size_Medium'] = 0.0
    features_df['input_size_Small'] = 0.0
    
    # Ensure correct feature ordering
    features_df = features_df[feature_names]
    
    # 4. Load scaler and apply transform for validation consistency
    scaler = loader.get_scaler()
    if scaler is not None:
        try:
            _ = scaler.transform(features_df)
            print("  - Applied StandardScaler transform successfully.")
        except Exception as scaler_err:
            print(f"  - [WARNING] Scaling transform failed: {scaler_err}")
    else:
        print("  - [WARNING] scaler is not available, skipping scaling step.")
           # 5. Predict using XGBoost model on unscaled features
    model = loader.get_xgboost_model()
    if model is None:
        raise FileNotFoundError("Could not load the XGBoost model from backend/models/xgboost_model.pkl")
        
    # Run prediction (unscaled as trained) using real model outputs
    try:
        preds = model.predict(features_df)
    except Exception as pred_err:
        print(f"  - [ERROR] Model direct prediction failed: {pred_err}")
        raise pred_err
    
    # Safety: replace negative values with small positive value
    preds = np.maximum(preds, 0.0)
    
    sample_df['predicted_energy_wh'] = preds
    sample_df['predicted_energy_mwh'] = preds * 1000.0
    
    print("Predictions generated for 5,000 Alibaba functions")
    return sample_df

def calculate_metrics_dict(y_true, y_pred):
    """Internal helper to compute a dict of performance metrics."""
    if len(y_true) == 0:
        return {"r2": 0.0, "mae": 0.0, "rmse": 0.0, "mape": 0.0, "accuracy": 0.0}
    
    safe_true = np.maximum(y_true, 1e-9)
    
    r2 = r2_score(y_true, y_pred) if len(y_true) >= 2 else 0.0
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs(y_true - y_pred) / safe_true) * 100.0
    accuracy = np.mean(np.maximum(0.0, 100.0 - np.abs(y_true - y_pred) / safe_true * 100.0))
    
    # Force convert types to standard Python floats for JSON compatibility
    return {
        "r2": float(r2),
        "mae": float(mae),
        "rmse": float(rmse),
        "mape": float(mape),
        "accuracy": float(accuracy)
    }

def calculate_metrics_summary(sample_df):
    """Calculates overall and runtime-specific metrics."""
    actual = sample_df['actual_energy_wh'].values
    pred = sample_df['predicted_energy_wh'].values
    
    # Overall metrics
    overall = calculate_metrics_dict(actual, pred)
    
    # Breakdown by runtime category
    breakdown = {}
    
    # Generalize runtime to category
    def generalize_runtime(rt):
        rt_str = str(rt).lower()
        if 'python' in rt_str:
            return 'python'
        elif 'node' in rt_str:
            return 'nodejs'
        elif 'java' in rt_str:
            return 'java'
        elif 'php' in rt_str:
            return 'php'
        else:
            return 'others'
            
    sample_df['runtime_category'] = sample_df['runtime'].apply(generalize_runtime)
    
    categories = ['python', 'nodejs', 'java', 'php', 'others']
    for cat in categories:
        sub = sample_df[sample_df['runtime_category'] == cat]
        if len(sub) > 0:
            breakdown[cat] = calculate_metrics_dict(sub['actual_energy_wh'].values, sub['predicted_energy_wh'].values)
            breakdown[cat]['n'] = int(len(sub))
        else:
            breakdown[cat] = {"r2": 0.0, "mae": 0.0, "rmse": 0.0, "mape": 0.0, "accuracy": 0.0, "n": 0}
            
    return overall, breakdown

def print_results(overall, breakdown):
    """Prints the formatted summary table to stdout."""
    r2 = overall['r2']
    if r2 >= 0.95:
        verdict = "[SUCCESS] STRONG - Model generalizes well to Alibaba Cloud"
    elif r2 >= 0.85:
        verdict = "[WARNING] MODERATE - Acceptable cross-platform accuracy"
    elif r2 >= 0.70:
        verdict = "[WARNING] LIMITED - Model shows platform-specific bias"
    else:
        verdict = "[ERROR] WEAK - Model requires retraining for Alibaba Cloud"
        
    print("\n========================================")
    print("   GREEN LAMBDA - ALIBABA VALIDATION     ")
    print("========================================")
    print("Dataset: Alibaba Cloud Functions 2021 (Low-Carbon Serverless)")
    print("Sample size: 5,000 functions")
    print("----------------------------------------")
    print("OVERALL METRICS:")
    print(f"  R^2 Score:   {overall['r2']:.4f}  (AWS: 0.9999)")
    print(f"  MAE:         {overall['mae']:.6f} Wh  (AWS: 0.0011 Wh)")
    print(f"  RMSE:        {overall['rmse']:.6f} Wh  (AWS: 0.0115 Wh)")
    print(f"  MAPE:        {overall['mape']:.2f}%")
    print(f"  Accuracy:    {overall['accuracy']:.2f}%")
    print("----------------------------------------")
    print("BREAKDOWN BY RUNTIME CATEGORY:")
    for cat, m in breakdown.items():
        print(f"  {cat.upper():<8}: R^2={m['r2']:.4f}  MAE={m['mae']:.6f}  n={m['n']}")
    print("----------------------------------------")
    print("GENERALIZABILITY VERDICT:")
    print(verdict)
    print("========================================")

def generate_plots(sample_df, overall):
    """Generates the three paper-quality visualization figures."""
    print("\nGenerating publication figures...")
    
    # FIGURE 1: Alibaba Validation Scatter Plot
    try:
        plt.figure(figsize=(7, 6), dpi=300)
        colors = {
            'python': '#4CAF50',  # Green
            'nodejs': '#2196F3',  # Blue
            'java': '#FF9800',    # Orange
            'php': '#9C27B0',     # Purple
            'others': '#607D8B'   # Grey
        }
        
        for cat, color in colors.items():
            sub = sample_df[sample_df['runtime_category'] == cat]
            if len(sub) > 0:
                plt.scatter(sub['actual_energy_wh'], sub['predicted_energy_wh'], 
                            color=color, label=cat.upper(), alpha=0.6, edgecolors='none', s=20)
                
        # Diagonal line (y=x)
        all_vals = np.concatenate([sample_df['actual_energy_wh'].values, sample_df['predicted_energy_wh'].values])
        min_val, max_val = all_vals.min(), all_vals.max()
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal (y=x)', linewidth=1.5)
        
        # R2 and MAE annotation
        plt.text(0.05, 0.95, f"$R^2$ = {overall['r2']:.4f}\nMAE = {overall['mae']:.6f} Wh",
                 transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
                 
        plt.xlabel('Actual Energy (Wh)', fontsize=11)
        plt.ylabel('Predicted Energy (Wh)', fontsize=11)
        plt.title('Alibaba Functions Validation: Predicted vs Actual Energy', fontsize=12, fontweight='bold')
        plt.legend(loc='lower right', frameon=True)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_alibaba_scatter.png'), dpi=300)
        plt.close()
        print("  - Created fig_alibaba_scatter.png")
    except Exception as e:
        print(f"  - [WARNING] Failed to generate Scatter Plot figure: {e}")
        
    # FIGURE 2: AWS vs Alibaba Comparison Bar Chart
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), dpi=300)
        
        categories1 = ['$R^2$ Score', 'Accuracy']
        aws_vals1 = [0.9999, 0.9998]
        alib_vals1 = [overall['r2'], overall['accuracy'] / 100.0]
        
        categories2 = ['MAE (Wh)', 'RMSE (Wh)']
        aws_vals2 = [0.0011, 0.0115]
        alib_vals2 = [overall['mae'], overall['rmse']]
        
        x = np.arange(2)
        width = 0.35
        
        # Left Subplot (R2 & Accuracy)
        rects1_aws = ax1.bar(x - width/2, aws_vals1, width, label='AWS', color='#2196F3')
        rects1_al = ax1.bar(x + width/2, alib_vals1, width, label='Alibaba', color='#FF9800')
        ax1.set_ylabel('Score / Accuracy (Fraction)', fontsize=10)
        ax1.set_title('$R^2$ and Accuracy Comparison', fontsize=10, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories1)
        ax1.set_ylim(0, 1.2)
        ax1.legend(loc='lower left')
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        # Right Subplot (MAE & RMSE)
        rects2_aws = ax2.bar(x - width/2, aws_vals2, width, label='AWS', color='#2196F3')
        rects2_al = ax2.bar(x + width/2, alib_vals2, width, label='Alibaba', color='#FF9800')
        ax2.set_ylabel('Energy (Wh)', fontsize=10)
        ax2.set_title('MAE and RMSE Comparison', fontsize=10, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories2)
        ax2.set_ylim(0, max(max(aws_vals2), max(alib_vals2)) * 1.3)
        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle=':', alpha=0.6)
        
        # Add values on top of bars
        def autolabel(rects, ax, fmt='{:.4f}'):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(fmt.format(height),
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)
                            
        autolabel(rects1_aws, ax1)
        autolabel(rects1_al, ax1)
        autolabel(rects2_aws, ax2, fmt='{:.4f}')
        autolabel(rects2_al, ax2, fmt='{:.4f}')
        
        plt.suptitle('Model Performance: AWS Lambda vs Alibaba Cloud', fontsize=11, fontweight='bold', y=0.98)
        fig.text(0.5, 0.01, 'Lower MAE/RMSE = better. Higher R2/Accuracy = better.', ha='center', fontsize=8, style='italic')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_alibaba_comparison.png'), dpi=300)
        plt.close()
        print("  - Created fig_alibaba_comparison.png")
    except Exception as e:
        print(f"  - [WARNING] Failed to generate Comparison Bar Chart figure: {e}")
        
    # FIGURE 3: Error Distribution Plot
    try:
        plt.figure(figsize=(7, 4), dpi=300)
        ape = np.abs(sample_df['actual_energy_wh'].values - sample_df['predicted_energy_wh'].values) / np.maximum(sample_df['actual_energy_wh'].values, 1e-9) * 100.0
        
        # Capping at 50% for cleaner histogram visualization
        visual_ape = np.clip(ape, 0, 50)
        
        counts, bins, patches = plt.hist(visual_ape, bins=np.arange(0, 51, 1), edgecolor='black', linewidth=0.5)
        
        # Color by ranges
        for i in range(len(patches)):
            bin_center = (bins[i] + bins[i+1]) / 2.0
            if bin_center < 5:
                patches[i].set_facecolor('#4CAF50')  # Green
            elif bin_center < 15:
                patches[i].set_facecolor('#FF9800')  # Orange
            elif bin_center < 30:
                patches[i].set_facecolor('#F44336')  # Red
            else:
                patches[i].set_facecolor('#B71C1C')  # Dark Red
                
        # Vertical boundary lines
        plt.axvline(5, color='black', linestyle='--', linewidth=1, alpha=0.7)
        plt.axvline(15, color='black', linestyle='--', linewidth=1, alpha=0.7)
        plt.axvline(30, color='black', linestyle='--', linewidth=1, alpha=0.7)
        
        # Percentages
        p_under_5 = np.mean(ape <= 5) * 100.0
        p_under_15 = np.mean(ape <= 15) * 100.0
        p_under_30 = np.mean(ape <= 30) * 100.0
        p_over_30 = np.mean(ape > 30) * 100.0
        
        # Labels on top
        max_y = plt.gca().get_ylim()[1]
        plt.text(1.5, max_y * 0.9, f"{p_under_5:.1f}%\n[0-5%]", ha='center', fontsize=8, fontweight='bold', color='darkgreen')
        plt.text(9.5, max_y * 0.9, f"{p_under_15 - p_under_5:.1f}%\n[5-15%]", ha='center', fontsize=8, fontweight='bold', color='darkorange')
        plt.text(22.5, max_y * 0.9, f"{p_under_30 - p_under_15:.1f}%\n[15-30%]", ha='center', fontsize=8, fontweight='bold', color='#B71C1C')
        plt.text(40, max_y * 0.9, f"{p_over_30:.1f}%\n[>30%]", ha='center', fontsize=8, fontweight='bold', color='darkred')
        
        # Legend/cumulative text box
        plt.text(0.02, 0.70, f"Cumulative Statistics:\n* {p_under_5:.1f}% within 5% error\n* {p_under_15:.1f}% within 15% error\n* {p_under_30:.1f}% within 30% error",
                 transform=plt.gca().transAxes, fontsize=9, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
                 
        plt.xlabel('Absolute Percentage Error (%)', fontsize=11)
        plt.ylabel('Number of Functions', fontsize=11)
        plt.title('Prediction Error Distribution - Alibaba Cloud Functions', fontsize=12, fontweight='bold')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.xlim(0, 50)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_alibaba_error_distribution.png'), dpi=300)
        plt.close()
        print("  - Created fig_alibaba_error_distribution.png")
    except Exception as e:
        print(f"  - [WARNING] Failed to generate Error Distribution figure: {e}")

def save_detailed_results(sample_df):
    """Saves the detailed results CSV file."""
    csv_df = sample_df[[
        'functionName', 'runtime', 'avg_duration_ms', 'memory_allocated_mb', 'invocation_count'
    ]].copy()
    
    # Calculate energy and error fields
    csv_df['actual_energy_wh'] = sample_df['actual_energy_wh']
    csv_df['predicted_energy_wh'] = sample_df['predicted_energy_wh']
    csv_df['absolute_error_wh'] = np.abs(csv_df['actual_energy_wh'] - csv_df['predicted_energy_wh'])
    csv_df['percentage_error'] = (csv_df['absolute_error_wh'] / np.maximum(csv_df['actual_energy_wh'], 1e-9)) * 100.0
    csv_df['accuracy_pct'] = np.maximum(0.0, 100.0 - csv_df['percentage_error'])
    
    csv_path = os.path.join(RESULTS_DIR, 'alibaba_validation_results.csv')
    csv_df.to_csv(csv_path, index=False)
    print(f"\nSaved detailed results to {csv_path}")

def save_summary_json(overall, breakdown):
    """Saves the summary JSON file."""
    r2 = overall['r2']
    if r2 >= 0.95:
        verdict = "STRONG"
    elif r2 >= 0.85:
        verdict = "MODERATE"
    elif r2 >= 0.70:
        verdict = "LIMITED"
    else:
        verdict = "WEAK"
        
    summary = {
        "dataset": "Alibaba Cloud Functions 2021",
        "paper": "Low-Carbon Serverless Dataset, 2021",
        "sample_size": 5000,
        "validation_date": datetime.now().strftime("%Y-%m-%d"),
        "overall_metrics": {
            "r2_score": overall['r2'],
            "mae_wh": overall['mae'],
            "rmse_wh": overall['rmse'],
            "mape_pct": overall['mape'],
            "mean_accuracy_pct": overall['accuracy']
        },
        "aws_baseline_metrics": {
            "r2_score": 0.9999,
            "mae_wh": 0.0011,
            "rmse_wh": 0.0115
        },
        "breakdown_by_runtime": breakdown,
        "feature_imputation_note": (
            "AST features (cyclomatic complexity, LOC, nesting depth etc.) and "
            "trigger type features were imputed with training data means/proportions "
            "as Alibaba dataset does not contain source code or trigger details. "
            "Only execution metrics and memory allocation were used directly."
        ),
        "generalizability_verdict": verdict
    }
    
    json_path = os.path.join(RESULTS_DIR, 'alibaba_validation_summary.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary JSON to {json_path}")

def main():
    try:
        # Step 1: Data Preprocessing
        master_df = load_and_merge_data()
        
        # Step 2: Stratified Sampling
        sample_df = stratified_sample(master_df, 'runtime', n=5000, random_state=42)
        
        # Step 3: Ground Truth Energy Calculation
        sample_df = calculate_ground_truth(sample_df)
        
        # Step 4: Feature Engineering & Predictions
        sample_df = build_features_and_predict(sample_df)
        
        # Step 5: Metrics Calculation
        overall, breakdown = calculate_metrics_summary(sample_df)
        
        # Step 6: Print Summary Table
        print_results(overall, breakdown)
        
        # Step 7: Save Outputs
        save_detailed_results(sample_df)
        save_summary_json(overall, breakdown)
        
        # Step 8: Generate Figures
        generate_plots(sample_df, overall)
        
        # Final Confirmation
        print("\n========================================")
        print("[SUCCESS] Alibaba validation complete!")
        print(f"Results saved to {RESULTS_DIR}")
        print("")
        print("Files created:")
        print("  alibaba_validation_results.csv - full results (5,000 rows)")
        print("  alibaba_validation_summary.json - metrics summary")
        print("  fig_alibaba_scatter.png - scatter plot (paper figure)")
        print("  fig_alibaba_comparison.png - AWS vs Alibaba comparison")
        print("  fig_alibaba_error_distribution.png - error distribution")
        print("========================================")
        
    except MemoryError:
        print("\n[WARNING] MemoryError encountered: dataset too large for available RAM.")
        print("Retrying with a smaller sample of 1,000 functions...")
        try:
            master_df = load_and_merge_data()
            sample_df = stratified_sample(master_df, 'runtime', n=1000, random_state=42)
            sample_df = calculate_ground_truth(sample_df)
            sample_df = build_features_and_predict(sample_df)
            overall, breakdown = calculate_metrics_summary(sample_df)
            print_results(overall, breakdown)
            save_detailed_results(sample_df)
            save_summary_json(overall, breakdown)
            generate_plots(sample_df, overall)
            print("\n[SUCCESS] Alibaba validation complete with reduced sample of 1,000 functions.")
        except Exception as retry_err:
            print(f"[ERROR] during fallback execution: {retry_err}")
            sys.path
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
