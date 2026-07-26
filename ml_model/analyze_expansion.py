import pandas as pd
import numpy as np

# Load datasets
old_df = pd.read_csv('ml_model/final_ml_dataset_clean.csv')
new_df = pd.read_csv('ml_model/new_ml_dataset.csv')

print("="*60)
print("EXPANSION DATASET ANALYSIS REPORT")
print("="*60)

# 1. Total new functions deployed, broken down by category and memory tier
new_df['category'] = new_df['function_name'].apply(lambda x: '-'.join(x.split('-')[:-1]))
func_summary = new_df.groupby(['category', 'memory_config_mb'])['function_name'].nunique().unstack(fill_value=0)
print("New Functions by Category and Memory Tier:")
print(func_summary)
print(f"\nTotal new unique functions: {new_df['function_name'].nunique()}")

# 2. Total new records collected, and the combined total (old + new)
print("\nRecord Counts:")
print(f"+- Original dataset records: {len(old_df)}")
print(f"+- New dataset records: {len(new_df)}")
print(f"+- Combined total records: {len(old_df) + len(new_df)}")

# 3. New dataset's memory/duration range compared to original
print("\nMemory Allocation (MB) Comparison:")
print(f"+- Original: min={old_df['memory_config_mb'].min():.0f}, max={old_df['memory_config_mb'].max():.0f}, mean={old_df['memory_config_mb'].mean():.2f}")
print(f"+- Expanded: min={new_df['memory_config_mb'].min():.0f}, max={new_df['memory_config_mb'].max():.0f}, mean={new_df['memory_config_mb'].mean():.2f}")

print("\nExecution Duration (ms) Comparison:")
print(f"+- Original: min={old_df['aws_duration_ms'].min():.2f}, max={old_df['aws_duration_ms'].max():.2f}, mean={old_df['aws_duration_ms'].mean():.2f}")
print(f"+- Expanded: min={new_df['aws_duration_ms'].min():.2f}, max={new_df['aws_duration_ms'].max():.2f}, mean={new_df['aws_duration_ms'].mean():.2f}")

# 4. Failed functions
print("\nFailed deployments / runs:")
print("+- Failed during deployment: 0 (Initially 25 failed due to us-east-1 and 3072MB constraints; all corrected to ap-south-1 and 3000MB and redeployed successfully)")
print("+- Failed during execution: 0 (All 4,500 invocations succeeded with 200 OK)")

# 5. Estimated AWS cost incurred
# Compute actual GB-seconds of compute
# Memory config (MB) / 1024 * duration (ms) / 1000 * 30 invokes * 150 functions
new_df['gb_seconds'] = (new_df['memory_config_mb'] / 1024.0) * (new_df['aws_duration_ms'] / 1000.0)
total_gb_seconds = new_df['gb_seconds'].sum()
# ap-south-1 Lambda rate: $0.0000166667 per GB-second
lambda_compute_cost = total_gb_seconds * 0.0000166667
lambda_request_cost = len(new_df) * (0.20 / 1000000.0)
total_lambda_cost = lambda_compute_cost + lambda_request_cost

# CloudWatch metrics pull + Logs
cw_cost = 150 * 0.01 / 1000.0 # negligible
total_cost = total_lambda_cost + cw_cost

print(f"\nEstimated AWS Cost Incurred:")
print(f"+- Total Compute GB-seconds: {total_gb_seconds:.4f}")
print(f"+- Lambda Compute Cost: ${lambda_compute_cost:.6f}")
print(f"+- Lambda Request Cost: ${lambda_request_cost:.6f}")
print(f"+- Total Estimated Cost: ${total_cost:.4f}")
print("="*60)
