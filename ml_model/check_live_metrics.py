import os
import boto3
import json
import requests
import tempfile
import zipfile
import pandas as pd
from datetime import datetime, timedelta
from radon.complexity import cc_visit

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'final_ml_dataset_clean.csv')
NEW_DATA_FILE = os.path.join(BASE_DIR, 'ml_model', 'new_ml_dataset.csv')
fn_name = 'etl-transform-10'

# 1. Get Static Dataset Values
df_orig = pd.read_csv(ORIG_DATA_FILE)
df_new = pd.read_csv(NEW_DATA_FILE)
df = pd.concat([df_orig, df_new], ignore_index=True)
func_rows = df[df['function_name'] == fn_name]

print("--- STATIC DATASET VALUES ---")
if len(func_rows) > 0:
    row = func_rows.iloc[0]
    print(f"aws_duration_ms: {row['aws_duration_ms']}")
    print(f"lines_of_code: {row['lines_of_code']}")
    print(f"cyclomatic_complexity: {row['cyclomatic_complexity']}")
else:
    print(f"{fn_name} not found in dataset!")

print("\n--- LIVE AWS VALUES ---")
try:
    # Load AWS Credentials like invoke_benchmarks.py does
    json_path = os.path.join(BASE_DIR, "backend", "aws_session.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    access_key = data.get("accessKeyId")
    secret_key = data.get("secretAccessKey")
    region = data.get("region")

    cw = boto3.client('cloudwatch', 
                      aws_access_key_id=access_key, 
                      aws_secret_access_key=secret_key, 
                      region_name=region)
    lb = boto3.client('lambda', 
                      aws_access_key_id=access_key, 
                      aws_secret_access_key=secret_key, 
                      region_name=region)

    # 1. Live Duration
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=14)
    cw_res = cw.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Duration',
        Dimensions=[{'Name': 'FunctionName', 'Value': fn_name}],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=['Average']
    )
    
    if cw_res['Datapoints']:
        live_duration_ms = sum(dp['Average'] for dp in cw_res['Datapoints']) / len(cw_res['Datapoints'])
        print(f"Live CloudWatch Duration (aws_duration_ms): {live_duration_ms}")
    else:
        print("No live CloudWatch duration datapoints found.")

    # 2. Live AST
    fn_info = lb.get_function(FunctionName=fn_name)
    code_url = fn_info['Code']['Location']
    r = requests.get(code_url, timeout=10)
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, 'lambda_code.zip')
        with open(zip_path, 'wb') as f:
            f.write(r.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        total_loc = 0
        complexities = []
        for root, dirs, files in os.walk(tmpdir):
            for file in files:
                if file.endswith('.py'):
                    py_path = os.path.join(root, file)
                    with open(py_path, 'r', encoding='utf-8') as pyf:
                        content = pyf.read()
                        lines = content.splitlines()
                        total_loc += len([line for line in lines if line.strip() and not line.strip().startswith('#')])
                        
                        try:
                            blocks = cc_visit(content)
                            if blocks:
                                complexities.extend([b.complexity for b in blocks])
                        except:
                            pass
                            
        live_loc = total_loc
        live_cc = (sum(complexities) / len(complexities)) if complexities else 1.0
        print(f"Live lines_of_code: {live_loc}")
        print(f"Live cyclomatic_complexity: {live_cc}")

except Exception as e:
    print(f"Error fetching live data: {e}")
