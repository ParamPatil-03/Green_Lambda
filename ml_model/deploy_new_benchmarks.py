import os
import boto3
import zipfile
import time
import json
import sys

def load_credentials():
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
    
    if access_key and secret_key and region:
        return access_key, secret_key, region
        
    # Check local JSON file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, 'backend', 'aws_session.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('accessKeyId'), data.get('secretAccessKey'), data.get('region')
    return None, None, None

def deploy_new_lambdas():
    print("="*60)
    print("DEPLOYING 150 NEW GREENLAMBDA FUNCTIONS")
    print("="*60)
    
    access_key, secret_key, region = load_credentials()
    if not access_key or not secret_key or not region:
        print("[ERROR] AWS Credentials could not be loaded!")
        sys.exit(1)
        
    print(f"AWS Region: {region}")
    
    iam_client = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
    lambda_client = boto3.client('lambda', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

    role_name = 'GreenLambdaBenchmarkRole'
    try:
        role = iam_client.get_role(RoleName=role_name)
        role_arn = role['Role']['Arn']
        print(f"[*] Found existing IAM role: {role_arn}")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"[*] IAM Role '{role_name}' not found. Creating it now...")
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Action": "sts:AssumeRole", "Principal": {"Service": "lambda.amazonaws.com"}, "Effect": "Allow"}]
        }
        role = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
        )
        role_arn = role['Role']['Arn']
        print("Role created. Waiting 10 seconds for IAM propagation...")
        time.sleep(10)

    # Memory tiers to distribute cyclically
    memory_tiers = [128, 256, 512, 1024, 2048, 3000]
    
    bench_dir = 'benchmarks_v2'
    deployed_count = 0
    
    # Sort files to ensure deterministic assignment
    files = sorted([f for f in os.listdir(bench_dir) if f.endswith('.py')])
    
    for idx, filename in enumerate(files):
        func_name_on_aws = filename.replace('.py', '').replace('_', '-')
        file_path = os.path.join(bench_dir, filename)
        zip_path = os.path.join(bench_dir, filename.replace('.py', '.zip'))
        
        # Memory Tier Cyclic Assignment: index % 6
        memory_size = memory_tiers[idx % len(memory_tiers)]
        
        with open(zip_path, 'rb') as f:
            zipped_code = f.read()

        # Delete if exists to ensure clean slate
        try:
            lambda_client.delete_function(FunctionName=func_name_on_aws)
        except lambda_client.exceptions.ResourceNotFoundException:
            pass
        except Exception as delete_err:
            print(f"   [WARNING] Could not delete {func_name_on_aws}: {delete_err}")

        # Deploy
        print(f"[{deployed_count+1}/150] Deploying {func_name_on_aws} with {memory_size}MB...")
        try:
            lambda_client.create_function(
                FunctionName=func_name_on_aws,
                Runtime='python3.11',
                Role=role_arn,
                Handler=f"{filename.replace('.py', '')}.lambda_handler",
                Code={'ZipFile': zipped_code},
                Timeout=90,  # Widen timeout to 90s to allow longer-running variant runs to finish comfortably
                MemorySize=memory_size
            )
            deployed_count += 1
        except Exception as e:
            print(f"   [ERROR] Failed to deploy {func_name_on_aws}: {e}")
            
    print(f"\n[SUCCESS] Deployed {deployed_count} functions successfully.")
    print("="*60)

if __name__ == "__main__":
    deploy_new_lambdas()
