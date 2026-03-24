import pandas as pd
import pickle
import os
import json

os.chdir('c:/Users/PARAM/Desktop/mini project/')
df = pd.read_csv('ml_model/final_ml_dataset_clean.csv')
df_sampled = df.sample(60, random_state=42)

# Same dummy logic as backend app.py
X = pd.get_dummies(df_sampled.drop(columns=['energy_target_wh', 'local_energy_wh', 'aws_energy_estimate_wh', 'aws_cold_start']), columns=['function_name', 'function_type', 'input_size'], drop_first=True)

feature_names = pickle.load(open('backend/models/feature_names.pkl', 'rb'))
model = pickle.load(open('backend/models/xgboost_model.pkl', 'rb'))

for col in feature_names:
    if col not in X.columns:
        X[col] = 0

X = X[feature_names]

y_actual = df_sampled['energy_target_wh'].values
y_pred = model.predict(X)

data = [{"x": float(a), "y": float(p)} for a, p in zip(y_actual, y_pred)]

with open("backend/results/scatter_data.json", "w") as f:
    json.dump(data, f)
