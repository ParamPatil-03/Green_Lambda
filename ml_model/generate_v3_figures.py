import matplotlib.pyplot as plt
import numpy as np
import os

# Create figures directory if it doesn't exist
os.makedirs('figures', exist_ok=True)

# Models and Metrics
models = ['XGBoost', 'Random Forest', 'Neural Network']
metrics = ['RMSE', 'MAE', 'R²', 'MAPE (%)']

# Values
xgboost = [0.0255, 0.0047, 0.9998, 2.41]
rf = [0.0465, 0.0087, 0.9993, 6.70]
nn = [0.0288, 0.0189, 0.9997, 71.64]

data = [xgboost, rf, nn]

fig, axs = plt.subplots(2, 2, figsize=(12, 10))
axs = axs.flatten()

colors = ['tab:blue', 'tab:orange', 'tab:green']

for i, metric in enumerate(metrics):
    vals = [xgboost[i], rf[i], nn[i]]
    bars = axs[i].bar(models, vals, color=colors)
    axs[i].set_title(metric)
    # add labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        axs[i].text(bar.get_x() + bar.get_width()/2, yval, round(yval, 4), ha='center', va='bottom', fontsize=9)

fig.suptitle('Model Comparison (V3)', fontsize=16)
plt.tight_layout()
plt.savefig('figures/v3_model_comparison.png', dpi=300)
print("Saved figures/v3_model_comparison.png")

# Plot 2: Cross-Platform Comparison
plt.close(fig)

platforms = ['AWS', 'Alibaba', 'Azure']
r2_scores = [0.9998, 0.6997, -2.497]

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [3, 1]})
plt.subplots_adjust(hspace=0.05)

ax1.bar(platforms, r2_scores, color=['tab:blue', 'tab:orange', 'tab:red'])
ax2.bar(platforms, r2_scores, color=['tab:blue', 'tab:orange', 'tab:red'])

ax1.set_ylim(0.0, 1.2)  
ax2.set_ylim(-3.0, -2.0)  

ax1.spines['bottom'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax1.xaxis.tick_top()
ax1.tick_params(labeltop=False)  
ax2.xaxis.tick_bottom()

d = .015  
kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
ax1.plot((-d, +d), (-d, +d), **kwargs)        
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  
kwargs.update(transform=ax2.transAxes)  
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  
ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  

for bar in ax1.patches:
    yval = bar.get_height()
    if yval > 0:
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 4), ha='center', va='bottom', fontsize=10)

for bar in ax2.patches:
    yval = bar.get_height()
    if yval < 0:
        ax2.text(bar.get_x() + bar.get_width()/2, yval - 0.2, round(yval, 4), ha='center', va='top', fontsize=10)

fig.suptitle('Cross-Platform Validation R² (V3)', fontsize=14)
fig.text(0.04, 0.5, 'R² Score', va='center', rotation='vertical', fontsize=12)
plt.savefig('figures/v3_crossplatform.png', dpi=300, bbox_inches='tight')
print("Saved figures/v3_crossplatform.png")
