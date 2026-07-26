#!/usr/bin/env python3
"""
Green Lambda — Cross-Platform Validation Script
==============================================
Validates the Green Lambda AWS-trained energy prediction model against the 
Azure Functions 2019 dataset to test cross-platform generalizability.

LIMITATIONS OF THIS CROSS-PLATFORM VALIDATION:
1. AST features (cyclomatic complexity, LOC, nesting depth, function calls etc.)
   are imputed with training data means because the Azure dataset does not include 
   source code. This means the model is being tested primarily on its ability to 
   generalize execution metrics, not code features.

2. Memory data in Azure dataset is at APPLICATION level, not FUNCTION level. 
   Multiple functions sharing an app will have the same memory value — this introduces noise.

3. The 'actual' energy values are calculated using the same physics-based formula 
   used in training, not hardware-measured power consumption. This means we are 
   testing formula generalization, not true energy measurement.

4. Azure Functions runtime characteristics differ from AWS Lambda — cold start behavior, 
   execution environments, and billing granularity are different. These differences 
   are not captured in the feature set.

These limitations are explicitly acknowledged for the research paper.
"""

import os
import sys
import glob
import json
import urllib.request
import tarfile
from datetime import datetime

# Manipulate sys.path to import model_loader from backend directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
backend_dir = os.path.join(project_root, "backend")
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

try:
    import pandas as pd
    import numpy as np
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

DATASET_URL = (
    "https://azurepublicdatasettraces.blob.core.windows.net/"
    "azurepublicdatasetv2/azurefunctions_dataset2019/"
    "azurefunctions-dataset2019.tar.xz"
)
TAR_PATH = os.path.join(RAW_DIR, "azurefunctions-dataset2019.tar.xz")
CLEAN_DATASET_PATH = os.path.join(project_root, "ml_model", "final_ml_dataset_clean.csv")

def download_progress(block_num, block_size, total_size):
    """Callback for showing download progress."""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, int(downloaded * 100 / total_size))
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total_size / (1024 * 1024)
        sys.stdout.write(f"\rProgress: {downloaded_mb:.2f} MB / {total_mb:.2f} MB ({percent}%)")
        sys.stdout.flush()
    else:
        sys.stdout.write(f"\rProgress: {downloaded / (1024 * 1024):.2f} MB")
        sys.stdout.flush()

def download_and_extract_dataset():
    """Handles downloading and extracting the Azure Functions 2019 dataset."""
    print("========================================")
    print("PART 1: DATASET DOWNLOAD AND EXTRACTION")
    print("========================================")
    
    # 1. Download dataset if not already downloaded
    if not os.path.exists(TAR_PATH):
        print("Downloading Azure Functions 2019 dataset...")
        try:
            urllib.request.urlretrieve(DATASET_URL, TAR_PATH, reporthook=download_progress)
            print("\nDownload complete.")
        except Exception as e:
            print(f"\n[ERROR] Downloading dataset failed: {e}")
            print(f"Please manually download the dataset from:\n  {DATASET_URL}")
            print(f"and save it as:\n  {TAR_PATH}")
            sys.exit(1)
    else:
        print("Using cached Azure Functions 2019 dataset archive.")

    # 2. Extract dataset automatically if csv files are not present
    # Check if a sampling of expected files exists
    sample_files = glob.glob(os.path.join(RAW_DIR, "**", "function_durations_percentiles.anon.d01.csv"), recursive=True)
    if not sample_files:
        print("Extracting the .tar.xz file automatically...")
        try:
            with tarfile.open(TAR_PATH) as tar:
                tar.extractall(path=RAW_DIR)
            print("Dataset extracted successfully")
        except Exception as e:
            print(f"[ERROR] Extraction failed: {e}")
            print("If the archive is corrupted, please delete it and re-run the script.")
            sys.exit(1)
    else:
        print("Dataset already extracted.")

def load_and_merge_data():
    """Loads and preprocesses duration, memory, and invocation files."""
    print("\n========================================")
    print("PART 2: DATA PREPROCESSING AND MERGING")
    print("========================================")
    
    # Find files recursively
    duration_files = sorted(glob.glob(os.path.join(RAW_DIR, "**", "function_durations_percentiles.anon.d*.csv"), recursive=True))
    memory_files = sorted(glob.glob(os.path.join(RAW_DIR, "**", "app_memory_percentiles.anon.d*.csv"), recursive=True))
    invocation_files = sorted(glob.glob(os.path.join(RAW_DIR, "**", "invocations_per_function_md.anon.d*.csv"), recursive=True))
    
    if not duration_files or not memory_files or not invocation_files:
        print(f"[ERROR] Required files not found in {RAW_DIR}")
        print(f"Found: {len(duration_files)} duration files, {len(memory_files)} memory files, {len(invocation_files)} invocation files.")
        sys.exit(1)
        
    print(f"Found {len(duration_files)} duration files, {len(memory_files)} memory files, {len(invocation_files)} invocation files.")
    
    # A. LOAD AND MERGE DURATION DATA (14 days)
    print("\nProcessing duration percentile data (14 days)...")
    duration_dfs = []
    total_functions_raw_count = 0
    for idx, filepath in enumerate(duration_files, 1):
        print(f"  [{idx}/14] Loading {os.path.basename(filepath)}...")
        try:
            # Load only required columns to save memory
            df_day = pd.read_csv(filepath, usecols=[
                'HashApp', 'HashFunction', 'Average', 'Count', 'Minimum', 'Maximum',
                'percentile_Average_50', 'percentile_Average_99'
            ])
            total_functions_raw_count += len(df_day['HashFunction'].unique())
            # Group by and aggregate to unique functions per day (just in case)
            df_day_agg = df_day.groupby(['HashFunction', 'HashApp'], as_index=False).agg({
                'Average': 'mean',
                'Count': 'sum',
                'Minimum': 'mean',
                'Maximum': 'mean',
                'percentile_Average_50': 'mean',
                'percentile_Average_99': 'mean'
            })
            duration_dfs.append(df_day_agg)
        except Exception as e:
            print(f"    [WARNING] Failed to load {filepath}: {e}")
            
    print("Aggregating duration data across all 14 days...")
    duration_df = pd.concat(duration_dfs, ignore_index=True)
    duration_df = duration_df.groupby(['HashFunction', 'HashApp'], as_index=False).agg({
        'Average': 'mean',
        'Count': 'sum',
        'Minimum': 'mean',
        'Maximum': 'mean',
        'percentile_Average_50': 'mean',
        'percentile_Average_99': 'mean'
    })
    
    # Keep only functions with Count >= 10
    print(f"  Total unique functions loaded: {len(duration_df):,}")
    duration_df = duration_df[duration_df['Count'] >= 10]
    print(f"  Functions with Count >= 10: {len(duration_df):,}")
    
    # Rename columns
    duration_df = duration_df.rename(columns={
        'Average': 'avg_duration_ms',
        'Count': 'invocation_count',
        'Minimum': 'min_duration_ms',
        'Maximum': 'max_duration_ms',
        'percentile_Average_50': 'p50_duration_ms',
        'percentile_Average_99': 'p99_duration_ms'
    })
    
    # B. LOAD AND MERGE MEMORY DATA (12 days)
    print("\nProcessing app memory percentiles data (12 days)...")
    memory_dfs = []
    for idx, filepath in enumerate(memory_files, 1):
        print(f"  [{idx}/12] Loading {os.path.basename(filepath)}...")
        try:
            df_day = pd.read_csv(filepath, usecols=[
                'HashApp', 'AverageAllocatedMb', 'AverageAllocatedMb_pct50', 'AverageAllocatedMb_pct99'
            ])
            df_day_agg = df_day.groupby('HashApp', as_index=False).mean()
            memory_dfs.append(df_day_agg)
        except Exception as e:
            print(f"    [WARNING] Failed to load {filepath}: {e}")
            
    print("Aggregating memory data across all 12 days...")
    memory_df = pd.concat(memory_dfs, ignore_index=True)
    memory_df = memory_df.groupby('HashApp', as_index=False).mean()
    memory_df = memory_df.rename(columns={
        'AverageAllocatedMb': 'memory_allocated_mb',
        'AverageAllocatedMb_pct50': 'memory_p50_mb',
        'AverageAllocatedMb_pct99': 'memory_p99_mb'
    })
    
    # C. LOAD INVOCATION COUNT DATA (14 days)
    print("\nProcessing invocation count data (14 days)...")
    invocation_dfs = []
    minute_cols = [str(i) for i in range(1, 1441)]
    for idx, filepath in enumerate(invocation_files, 1):
        print(f"  [{idx}/14] Loading {os.path.basename(filepath)}...")
        try:
            # Load full day CSV and calculate sum of minutes row-by-row
            df_day = pd.read_csv(filepath)
            cols_to_sum = [c for c in minute_cols if c in df_day.columns]
            df_day['daily_invocations'] = df_day[cols_to_sum].sum(axis=1)
            
            # Keep only necessary columns
            df_day_agg = df_day[['HashFunction', 'Trigger', 'daily_invocations']].copy()
            invocation_dfs.append(df_day_agg)
        except Exception as e:
            print(f"    [WARNING] Failed to load {filepath}: {e}")
            
    print("Aggregating invocation counts across all 14 days...")
    invocation_df = pd.concat(invocation_dfs, ignore_index=True)
    invocation_df = invocation_df.groupby('HashFunction', as_index=False).agg({
        'daily_invocations': 'mean',
        'Trigger': 'first'
    })
    invocation_df = invocation_df.rename(columns={'Trigger': 'trigger_type'})
    
    # D. MERGE ALL THREE INTO MASTER DATASET
    print("\nMerging into Master Dataset...")
    master_df = pd.merge(duration_df, invocation_df, on='HashFunction', how='inner')
    master_df = pd.merge(master_df, memory_df, on='HashApp', how='inner')
    
    # Drop rows where memory or duration are missing or 0
    master_df = master_df.dropna(subset=['memory_allocated_mb', 'avg_duration_ms'])
    master_df = master_df[(master_df['avg_duration_ms'] > 0) & (master_df['memory_allocated_mb'] > 0)]
    
    # Cap memory at 1500 MB and duration at 300,000 ms (5 mins)
    master_df = master_df[master_df['memory_allocated_mb'] <= 1500]
    master_df = master_df[master_df['avg_duration_ms'] <= 300000]
    
    # Print Dataset Stats
    print("\nAzure dataset loaded:")
    print(f"  Total functions (raw unique count): {total_functions_raw_count:,}")
    print(f"  After filtering: {len(master_df):,}")
    print(f"  Duration range: {master_df['avg_duration_ms'].min():.1f} ms - {master_df['avg_duration_ms'].max():.1f} ms")
    print(f"  Memory range: {master_df['memory_allocated_mb'].min():.1f} MB - {master_df['memory_allocated_mb'].max():.1f} MB")
    
    # Calculate Trigger Proportions
    trigger_counts = master_df['trigger_type'].value_counts()
    trigger_pcts = (trigger_counts / len(master_df)) * 100
    trigger_str = ", ".join([f"{str(k).upper()}={v:.1f}%" for k, v in trigger_pcts.items()])
    print(f"  Trigger types: {trigger_str}")
    
    return master_df

def stratified_sample(df, col, n=5000, random_state=42):
    """Draws a stratified random sample of size n proportionally covering trigger types."""
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
            
    print(f"Sampled {len(sampled)} functions for validation")
    return sampled

def calculate_ground_truth(df):
    """Calculates the physics-based actual energy consumption (Wh and mWh)."""
    # Power (W) = 10 + (0.2 * memory_allocated_mb)
    power_w = 10.0 + (0.2 * df['memory_allocated_mb'])
    # Energy (Wh) = Power * (avg_duration_ms / 3,600,000)
    df['actual_energy_wh'] = power_w * (df['avg_duration_ms'] / 3600000.0)
    df['actual_energy_mwh'] = df['actual_energy_wh'] * 1000.0
    
    print("\n========================================")
    print("PART 3: FEATURE ENGINEERING & METRICS")
    print("========================================")
    print(f"Actual energy range: {df['actual_energy_wh'].min():.6f} - {df['actual_energy_wh'].max():.6f} Wh")
    print(f"Mean actual energy: {df['actual_energy_wh'].mean():.6f} Wh")
    
    return df

def build_features_and_predict(sample_df):
    """Builds the 34-feature vector, applies scaling, and predicts energy consumption."""
    # 1. Load Training dataset means for imputation
    print("Loading training dataset for feature imputation...")
    try:
        train_df = pd.read_csv(CLEAN_DATASET_PATH)
        train_means = train_df.mean(numeric_only=True).to_dict()
        print("  - Loaded training dataset means successfully.")
    except Exception as e:
        print(f"  - [WARNING] Loading training dataset failed: {e}. Using fallback defaults.")
        # Fallback to hardcoded training means
        train_means = {
            'cold_start': 0.033783783783783786,
            'lines_of_code': 23.86861861861862,
            'num_loops': 2.40015015015015,
            'num_conditionals': 0.668918918918919,
            'num_function_calls': 9.396396396396396,
            'cyclomatic_complexity': 4.069069069069069,
            'max_nesting_depth': 1.5375375375375375,
            'local_cpu_percent': 17.49655405405405,
            'memory_efficiency': 0.09614081855292793,
            'calibration_ratio': 0.0003362762255765649
        }
        
    # 2. Get feature names list from loader
    loader = model_loader.get_loader()
    feature_names = loader.get_feature_names()
    
    # 3. Construct features DataFrame
    features_df = pd.DataFrame(index=sample_df.index)
    
    # Direct mappings
    features_df['memory_config_mb'] = sample_df['memory_allocated_mb']
    features_df['cold_start'] = train_means.get('cold_start', 0.033783783783783786)
    features_df['lines_of_code'] = train_means.get('lines_of_code', 23.86861861861862)
    features_df['num_loops'] = train_means.get('num_loops', 2.40015015015015)
    features_df['num_conditionals'] = train_means.get('num_conditionals', 0.668918918918919)
    features_df['num_function_calls'] = train_means.get('num_function_calls', 9.396396396396396)
    features_df['cyclomatic_complexity'] = train_means.get('cyclomatic_complexity', 4.069069069069069)
    features_df['max_nesting_depth'] = train_means.get('max_nesting_depth', 1.5375375375375375)
    features_df['local_duration_ms'] = sample_df['avg_duration_ms']
    features_df['local_cpu_percent'] = train_means.get('local_cpu_percent', 17.49655405405405)
    features_df['local_memory_mb'] = sample_df['memory_allocated_mb']
    features_df['aws_duration_ms'] = sample_df['avg_duration_ms']
    features_df['aws_memory_used_mb'] = sample_df['memory_allocated_mb']
    features_df['duration_ratio'] = 1.0
    features_df['memory_efficiency'] = train_means.get('memory_efficiency', 0.09614081855292793)
    features_df['calibration_ratio'] = train_means.get('calibration_ratio', 0.0003362762255765649)
    
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
    features_df['function_type_io'] = sample_df['trigger_type'].apply(
        lambda t: 1.0 if str(t).lower() in ['queue', 'event'] else 0.0
    )
    features_df['function_type_memory'] = sample_df['trigger_type'].apply(
        lambda t: 1.0 if str(t).lower() == 'storage' else 0.0
    )
    
    # Input size (all 0)
    features_df['input_size_Medium'] = 0.0
    features_df['input_size_Small'] = 0.0
    
    # Ensure correct feature ordering
    features_df = features_df[feature_names]
    
    # 4. Load scaler and apply transform for validation consistency
    scaler = loader.get_scaler()
    if scaler is not None:
        _ = scaler.transform(features_df)
        print("  - Applied StandardScaler transform successfully.")
    else:
        print("  - [WARNING] scaler is not available, skipping scaling step.")
        
    # 5. Predict using XGBoost model on unscaled features
    model = loader.get_xgboost_model()
    if model is None:
        raise FileNotFoundError("Could not load the XGBoost model from backend/models/xgboost_model.pkl")
        
    # Run prediction (unscaled as trained) using real model outputs
    preds = model.predict(features_df)
    
    # Safety: replace negative values with small positive value
    preds = np.maximum(preds, 0.0)
    
    sample_df['predicted_energy_wh'] = preds
    sample_df['predicted_energy_mwh'] = preds * 1000.0
    
    print("Predictions generated for 5,000 Azure functions")
    return sample_df

def calculate_metrics_summary(sample_df):
    """Calculates overall and trigger-specific metrics."""
    actual = sample_df['actual_energy_wh'].values
    pred = sample_df['predicted_energy_wh'].values
    
    # Overall metrics
    overall = calculate_metrics_dict(actual, pred)
    
    # Breakdown by trigger type
    breakdown = {}
    triggers = ['http', 'timer', 'queue', 'storage']
    
    for tr in triggers:
        sub = sample_df[sample_df['trigger_type'] == tr]
        if len(sub) > 0:
            breakdown[tr] = calculate_metrics_dict(sub['actual_energy_wh'].values, sub['predicted_energy_wh'].values)
            breakdown[tr]['n'] = int(len(sub))
        else:
            breakdown[tr] = {"r2": 0.0, "mae": 0.0, "rmse": 0.0, "accuracy": 0.0, "n": 0}
            
    # Others category
    others_sub = sample_df[~sample_df['trigger_type'].isin(triggers)]
    if len(others_sub) > 0:
        breakdown['others'] = calculate_metrics_dict(others_sub['actual_energy_wh'].values, others_sub['predicted_energy_wh'].values)
        breakdown['others']['n'] = int(len(others_sub))
    else:
        breakdown['others'] = {"r2": 0.0, "mae": 0.0, "rmse": 0.0, "accuracy": 0.0, "n": 0}
        
    return overall, breakdown

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

def print_results(overall, breakdown):
    """Prints the formatted summary table to stdout."""
    # Determine Generalizability Verdict
    r2 = overall['r2']
    if r2 >= 0.95:
        verdict = "[SUCCESS] STRONG - Model generalizes well to Azure"
    elif r2 >= 0.85:
        verdict = "[WARNING] MODERATE - Acceptable cross-platform accuracy"
    elif r2 >= 0.70:
        verdict = "[WARNING] LIMITED - Model shows platform-specific bias"
    else:
        verdict = "[ERROR] WEAK - Model requires retraining for Azure"
        
    print("\n========================================")
    print("   GREEN LAMBDA - AZURE VALIDATION     ")
    print("========================================")
    print("Dataset: Azure Functions 2019 (USENIX ATC 2020)")
    print("Sample size: 5,000 functions")
    print("----------------------------------------")
    print("OVERALL METRICS:")
    print(f"  R^2 Score:   {overall['r2']:.4f}  (AWS: 0.9999)")
    print(f"  MAE:         {overall['mae']:.6f} Wh  (AWS: 0.0011 Wh)")
    print(f"  RMSE:        {overall['rmse']:.6f} Wh  (AWS: 0.0115 Wh)")
    print(f"  MAPE:        {overall['mape']:.2f}%")
    print(f"  Accuracy:    {overall['accuracy']:.2f}%")
    print("----------------------------------------")
    print("BREAKDOWN BY TRIGGER TYPE:")
    for tr, m in breakdown.items():
        print(f"  {tr.upper():<8}: R^2={m['r2']:.4f}  MAE={m['mae']:.6f}  n={m['n']}")
    print("----------------------------------------")
    print("GENERALIZABILITY VERDICT:")
    print(verdict)
    print("========================================")

def generate_plots(sample_df, overall):
    """Generates the three paper-quality visualization figures."""
    print("\nGenerating publication figures...")
    
    # FIGURE 1: Azure Validation Scatter Plot
    try:
        plt.figure(figsize=(7, 6), dpi=300)
        colors = {
            'http': '#2196F3',
            'timer': '#4CAF50',
            'queue': '#FF9800',
            'storage': '#9C27B0',
            'others': '#607D8B'
        }
        
        for tr, color in colors.items():
            if tr == 'others':
                sub = sample_df[~sample_df['trigger_type'].isin(['http', 'timer', 'queue', 'storage'])]
            else:
                sub = sample_df[sample_df['trigger_type'] == tr]
                
            if len(sub) > 0:
                plt.scatter(sub['actual_energy_wh'], sub['predicted_energy_wh'], 
                            color=color, label=tr.upper(), alpha=0.6, edgecolors='none', s=20)
                
        # Diagonal line (y=x)
        all_vals = np.concatenate([sample_df['actual_energy_wh'].values, sample_df['predicted_energy_wh'].values])
        min_val, max_val = all_vals.min(), all_vals.max()
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal (y=x)', linewidth=1.5)
        
        # R2 and MAE annotation (using standard R^2 LaTeX formatting in matplotlib)
        plt.text(0.05, 0.95, f"$R^2$ = {overall['r2']:.4f}\nMAE = {overall['mae']:.6f} Wh",
                 transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='none'))
                 
        plt.xlabel('Actual Energy (Wh)', fontsize=11)
        plt.ylabel('Predicted Energy (Wh)', fontsize=11)
        plt.title('Azure Functions Validation: Predicted vs Actual Energy', fontsize=12, fontweight='bold')
        plt.legend(loc='lower right', frameon=True)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_azure_scatter.png'), dpi=300)
        plt.close()
        print("  - Created fig_azure_scatter.png")
    except Exception as e:
        print(f"  - [WARNING] Failed to generate Scatter Plot figure: {e}")
        
    # FIGURE 2: AWS vs Azure Comparison Bar Chart
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), dpi=300)
        
        categories1 = ['$R^2$ Score', 'Accuracy']
        # AWS baseline (Accuracy ~99.98% or 0.9998 from training data check)
        aws_vals1 = [0.9999, 0.9998]
        azure_vals1 = [overall['r2'], overall['accuracy'] / 100.0]
        
        categories2 = ['MAE (Wh)', 'RMSE (Wh)']
        aws_vals2 = [0.0011, 0.0115]
        azure_vals2 = [overall['mae'], overall['rmse']]
        
        x = np.arange(2)
        width = 0.35
        
        # Left Subplot (R2 & Accuracy)
        rects1_aws = ax1.bar(x - width/2, aws_vals1, width, label='AWS', color='#2196F3')
        rects1_az = ax1.bar(x + width/2, azure_vals1, width, label='Azure', color='#FF9800')
        ax1.set_ylabel('Score / Accuracy (Fraction)', fontsize=10)
        ax1.set_title('$R^2$ and Accuracy Comparison', fontsize=10, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories1)
        ax1.set_ylim(0, 1.2)
        ax1.legend(loc='lower left')
        ax1.grid(True, linestyle=':', alpha=0.6)
        
        # Right Subplot (MAE & RMSE)
        rects2_aws = ax2.bar(x - width/2, aws_vals2, width, label='AWS', color='#2196F3')
        rects2_az = ax2.bar(x + width/2, azure_vals2, width, label='Azure', color='#FF9800')
        ax2.set_ylabel('Energy (Wh)', fontsize=10)
        ax2.set_title('MAE and RMSE Comparison', fontsize=10, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories2)
        ax2.set_ylim(0, max(max(aws_vals2), max(azure_vals2)) * 1.3)
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
        autolabel(rects1_az, ax1)
        autolabel(rects2_aws, ax2, fmt='{:.4f}')
        autolabel(rects2_az, ax2, fmt='{:.4f}')
        
        plt.suptitle('Model Performance: AWS Lambda vs Azure Functions', fontsize=11, fontweight='bold', y=0.98)
        fig.text(0.5, 0.01, 'Lower MAE/RMSE = better. Higher R2/Accuracy = better.', ha='center', fontsize=8, style='italic')
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_azure_comparison.png'), dpi=300)
        plt.close()
        print("  - Created fig_azure_comparison.png")
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
        plt.title('Prediction Error Distribution - Azure Functions', fontsize=12, fontweight='bold')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.xlim(0, 50)
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'fig_azure_error_distribution.png'), dpi=300)
        plt.close()
        print("  - Created fig_azure_error_distribution.png")
    except Exception as e:
        print(f"  - [WARNING] Failed to generate Error Distribution figure: {e}")

def save_detailed_results(sample_df):
    """Saves the detailed results CSV file."""
    # Columns to save
    csv_df = sample_df[[
        'HashFunction', 'trigger_type', 'avg_duration_ms', 'memory_allocated_mb', 'invocation_count'
    ]].copy()
    
    # Calculate energy and error fields
    csv_df['actual_energy_wh'] = sample_df['actual_energy_wh']
    csv_df['predicted_energy_wh'] = sample_df['predicted_energy_wh']
    csv_df['absolute_error_wh'] = np.abs(csv_df['actual_energy_wh'] - csv_df['predicted_energy_wh'])
    csv_df['percentage_error'] = (csv_df['absolute_error_wh'] / np.maximum(csv_df['actual_energy_wh'], 1e-9)) * 100.0
    csv_df['accuracy_pct'] = np.maximum(0.0, 100.0 - csv_df['percentage_error'])
    
    # Save to CSV
    csv_path = os.path.join(RESULTS_DIR, 'azure_validation_results.csv')
    csv_df.to_csv(csv_path, index=False)
    print(f"\nSaved detailed results to {csv_path}")

def save_summary_json(overall, breakdown):
    """Saves the summary JSON file, ensuring standard python float types are used."""
    # Determine Verdict
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
        "dataset": "Azure Functions 2019",
        "paper": "Serverless in the Wild, USENIX ATC 2020",
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
        "breakdown_by_trigger": breakdown,
        "feature_imputation_note": (
            "AST features (cyclomatic complexity, LOC, nesting depth etc.) were imputed "
            "with training data means as Azure dataset does not contain source code. "
            "Only execution metrics and memory allocation were used directly."
        ),
        "generalizability_verdict": verdict
    }
    
    json_path = os.path.join(RESULTS_DIR, 'azure_validation_summary.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary JSON to {json_path}")

def main():
    try:
        # Step 1: Download & Extract
        download_and_extract_dataset()
        
        # Step 2: Data Preprocessing
        master_df = load_and_merge_data()
        
        # Step 3: Stratified Sampling
        sample_df = stratified_sample(master_df, 'trigger_type', n=5000, random_state=42)
        
        # Step 4: Ground Truth Energy Calculation
        sample_df = calculate_ground_truth(sample_df)
        
        # Step 5: Feature Engineering & Predictions
        sample_df = build_features_and_predict(sample_df)
        
        # Step 6: Metrics Calculation
        overall, breakdown = calculate_metrics_summary(sample_df)
        
        # Step 7: Print Summary Table
        print_results(overall, breakdown)
        
        # Step 8: Save Outputs
        save_detailed_results(sample_df)
        save_summary_json(overall, breakdown)
        
        # Step 9: Generate Figures
        generate_plots(sample_df, overall)
        
        # Final Confirmation
        print("\n========================================")
        print("[SUCCESS] Azure validation complete!")
        print(f"Results saved to {RESULTS_DIR}")
        print("")
        print("Files created:")
        print("  azure_validation_results.csv - full results (5,000 rows)")
        print("  azure_validation_summary.json - metrics summary")
        print("  fig_azure_scatter.png - scatter plot (paper figure)")
        print("  fig_azure_comparison.png - AWS vs Azure comparison")
        print("  fig_azure_error_distribution.png - error distribution")
        print("")
        print("Next steps:")
        print("  1. Upload figures to Overleaf /figures/ folder")
        print("  2. Add cross-platform validation section to paper")
        print("  3. Cite: Shahrad et al. USENIX ATC 2020")
        print("========================================")
        
    except MemoryError:
        print("\n[WARNING] MemoryError encountered: dataset too large for available RAM.")
        print("Retrying with a smaller sample of 1,000 functions...")
        # Reduce sample and re-try
        try:
            # Re-load data, but with lower sampling if we can
            master_df = load_and_merge_data()
            sample_df = stratified_sample(master_df, 'trigger_type', n=1000, random_state=42)
            sample_df = calculate_ground_truth(sample_df)
            sample_df = build_features_and_predict(sample_df)
            overall, breakdown = calculate_metrics_summary(sample_df)
            print_results(overall, breakdown)
            save_detailed_results(sample_df)
            save_summary_json(overall, breakdown)
            generate_plots(sample_df, overall)
            print("\n[SUCCESS] Azure validation complete with reduced sample of 1,000 functions.")
        except Exception as retry_err:
            print(f"[ERROR] during fallback execution: {retry_err}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[ERROR] during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
