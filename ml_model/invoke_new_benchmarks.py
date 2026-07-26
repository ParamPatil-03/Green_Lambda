import os
import boto3
import json
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_credentials():
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
    
    if access_key and secret_key and region:
        return access_key, secret_key, region
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'backend', 'aws_session.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('accessKeyId'), data.get('secretAccessKey'), data.get('region')
    return None, None, None

def invoke_function(lambda_client, func_name, invocation_id):
    try:
        # Simulate varying inputs slightly
        payload = {"test": True, "run_id": invocation_id, "route": "users" if invocation_id % 2 == 0 else "posts"}
        res = lambda_client.invoke(
            FunctionName=func_name,
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        status = res.get('StatusCode')
        return status == 202
    except Exception as e:
        print(f"Error invoking {func_name} (run {invocation_id}): {e}")
        return False

def invoke_all_benchmarks():
    print("="*60)
    print("WARMING UP AND INVOKING 150 GREENLAMBDA FUNCTIONS")
    print("="*60)
    
    access_key, secret_key, region = load_credentials()
    if not access_key or not secret_key or not region:
        print("[ERROR] AWS Credentials could not be loaded!")
        sys.exit(1)
        
    print(f"AWS Region: {region}")
    
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    # Generate list of 150 functions
    categories = ['etl-transform', 'image-proc', 'ml-inference', 'rest-api', 'scientific-calc']
    functions = []
    for cat in categories:
        for i in range(1, 31):
            functions.append(f"{cat}-{i:02d}")
            
    print(f"[*] Sourced {len(functions)} functions for invocation.")
    print("[*] Running 30 invocations per function in parallel (concurrency=15) to save time...")
    
    total_invocations = len(functions) * 30
    success_count = 0
    start_time = time.time()
    
    # Use ThreadPoolExecutor for fast concurrent invocations
    with ThreadPoolExecutor(max_workers=60) as executor:
        futures = []
        for idx, func in enumerate(functions):
            for run_id in range(1, 31):
                futures.append(executor.submit(invoke_function, lambda_client, func, run_id))
                
        completed = 0
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                success_count += 1
            completed += 1
            if completed % 300 == 0:
                print(f" Progress: {completed}/{total_invocations} invocations complete... ({success_count} success)")
                
    elapsed = time.time() - start_time
    print(f"\n[SUCCESS] Completed {total_invocations} invocations in {elapsed:.2f} seconds.")
    print(f"   Success: {success_count} | Failed: {total_invocations - success_count}")
    
    # Wait for CloudWatch metrics to settle
    settle_time = 140
    print(f"Waiting {settle_time} seconds for CloudWatch metrics to settle...")
    time.sleep(settle_time)
    print("[*] Telemetry is settled and ready for extraction.")
    print("="*60)

if __name__ == "__main__":
    invoke_all_benchmarks()
