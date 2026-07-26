#!/usr/bin/env python3
"""
Green Lambda Research Paper
===========================
Generates a publication-quality 2x2 comparison figure displaying the cross-platform 
generalizability of the energy prediction model across three serverless platforms:
1. AWS Lambda (Training Platform)
2. Azure Functions (Unseen Platform)
3. Alibaba Cloud Functions (Unseen Platform)
"""

import os
import json
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
except ImportError as e:
    print(f"Error importing required visualization packages: {e}")
    print("Please ensure matplotlib is installed in your python environment.")
    sys.exit(1)

# Set global Matplotlib parameters for research quality
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

def load_summary_json(filepath):
    """Safely loads and returns JSON data from filepath."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_value_labels(ax, rects, decimals=4):
    """Helper to add formatted text labels above each bar."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(
            f"{height:.{decimals}f}",
            xy=(rect.get_x() + rect.get_width() / 2, height),
            xytext=(0, 4),  # 4 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',
            fontsize=8, family='serif'
        )

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input paths
    azure_path = os.path.join(script_dir, "azure_validation", "results", "azure_validation_summary.json")
    alibaba_path = os.path.join(script_dir, "alibaba_validation", "results", "alibaba_validation_summary.json")
    
    # Define output path
    figures_dir = os.path.join(script_dir, "figures")
    output_path = os.path.join(figures_dir, "fig_three_platform_comparison.png")
    
    try:
        # Load validation data
        print("Reading platform validation results...")
        azure_data = load_summary_json(azure_path)
        alibaba_data = load_summary_json(alibaba_path)
        
        # Extract metrics dynamically from input JSON files
        r2_azure = azure_data['overall_metrics']['r2_score']
        r2_alibaba = alibaba_data['overall_metrics']['r2_score']
        
        acc_azure = azure_data['overall_metrics']['mean_accuracy_pct']
        acc_alibaba = alibaba_data['overall_metrics']['mean_accuracy_pct']
        
        mae_azure = azure_data['overall_metrics']['mae_wh']
        mae_alibaba = alibaba_data['overall_metrics']['mae_wh']
        
        rmse_azure = azure_data['overall_metrics']['rmse_wh']
        rmse_alibaba = alibaba_data['overall_metrics']['rmse_wh']
        
        # Hardcoded AWS Baseline Metrics
        r2_aws = 0.9999
        acc_aws = 99.00
        mae_aws = 0.0011
        rmse_aws = 0.0115
        
        # Align metrics
        platforms = ['AWS', 'Azure', 'Alibaba']
        colors = ['#2196F3', '#FF9800', '#4CAF50']
        
        r2_vals = [r2_aws, r2_azure, r2_alibaba]
        acc_vals = [acc_aws, acc_azure, acc_alibaba]
        mae_vals = [mae_aws, mae_azure, mae_alibaba]
        rmse_vals = [rmse_aws, rmse_azure, rmse_alibaba]
        
        # Create subplots
        fig, axs = plt.subplots(2, 2, figsize=(10, 8), dpi=300)
        
        # 1. TOP LEFT: R2 Score
        ax = axs[0, 0]
        rects = ax.bar(platforms, r2_vals, color=colors, width=0.5, edgecolor='black', linewidth=0.5)
        ax.set_ylabel("R² Score", fontsize=10, family='serif')
        ax.set_ylim(0.990, 1.001)
        ax.axhline(0.995, color='gray', linestyle='--', linewidth=0.8)
        add_value_labels(ax, rects, decimals=4)
        ax.grid(True, linestyle=':', alpha=0.5, axis='y')
        ax.tick_params(labelsize=9)
        
        # 2. TOP RIGHT: Mean Accuracy
        ax = axs[0, 1]
        rects = ax.bar(platforms, acc_vals, color=colors, width=0.5, edgecolor='black', linewidth=0.5)
        ax.set_ylabel("Mean Accuracy (%)", fontsize=10, family='serif')
        ax.set_ylim(90, 101)
        ax.axhline(95, color='gray', linestyle='--', linewidth=0.8)
        add_value_labels(ax, rects, decimals=2)
        ax.grid(True, linestyle=':', alpha=0.5, axis='y')
        ax.tick_params(labelsize=9)
        
        # 3. BOTTOM LEFT: MAE
        ax = axs[1, 0]
        rects = ax.bar(platforms, mae_vals, color=colors, width=0.5, edgecolor='black', linewidth=0.5)
        ax.set_ylabel("Mean Absolute Error (Wh)", fontsize=10, family='serif')
        ax.set_xlabel("(lower is better)", fontsize=9, style='italic', family='serif')
        ax.set_ylim(0, max(mae_vals) * 1.2)
        add_value_labels(ax, rects, decimals=6)
        ax.grid(True, linestyle=':', alpha=0.5, axis='y')
        ax.tick_params(labelsize=9)
        
        # 4. BOTTOM RIGHT: RMSE
        ax = axs[1, 1]
        rects = ax.bar(platforms, rmse_vals, color=colors, width=0.5, edgecolor='black', linewidth=0.5)
        ax.set_ylabel("Root Mean Square Error (Wh)", fontsize=10, family='serif')
        ax.set_xlabel("(lower is better)", fontsize=9, style='italic', family='serif')
        ax.set_ylim(0, max(rmse_vals) * 1.2)
        add_value_labels(ax, rects, decimals=6)
        ax.grid(True, linestyle=':', alpha=0.5, axis='y')
        ax.tick_params(labelsize=9)
        
        # Main title
        fig.suptitle("Cross-Platform Generalizability of Green Lambda", fontsize=14, fontweight='bold', family='serif', y=0.97)
        
        # Create shared legend
        aws_patch = mpatches.Patch(color='#2196F3', label='AWS Lambda (Training Platform)')
        azure_patch = mpatches.Patch(color='#FF9800', label='Azure Functions (Unseen Platform)')
        alibaba_patch = mpatches.Patch(color='#4CAF50', label='Alibaba Cloud (Unseen Platform)')
        
        fig.legend(
            handles=[aws_patch, azure_patch, alibaba_patch], 
            loc='lower center', ncol=3, frameon=True, fontsize=9, 
            bbox_to_anchor=(0.5, 0.05)
        )
        
        # Add shared note/caption below the legend
        fig.text(
            0.5, 0.02, 
            "Model trained on AWS data only. Azure and Alibaba tested without retraining.", 
            ha='center', fontsize=9, style='italic', family='serif'
        )
        
        # Ensure figures folder exists
        os.makedirs(figures_dir, exist_ok=True)
        
        # Apply tight layout with reserved space for suptitle and legend
        fig.tight_layout(rect=[0, 0.08, 1, 0.95])
        
        # Save output figure
        plt.savefig(output_path, dpi=300)
        plt.close()
        
        print("SUCCESS: Three platform comparison figure saved to:")
        print(f"\"{output_path}\"")
        print("Ready to upload to Overleaf figures/ folder")
        
    except FileNotFoundError as fnf_err:
        print(f"[ERROR] Required summary JSON file not found: {fnf_err}")
        print("Please check that the cross-platform validation scripts have been executed first.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to generate comparison figure: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
