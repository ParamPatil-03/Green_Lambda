import os
import boto3
import zipfile
import time
import json

def deploy_lambdas(access_key, secret_key, region):
    print("Setting up Boto3 Deployment (Upgrading to Python 3.11)...")
    iam_client = boto3.client('iam', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
    lambda_client = boto3.client('lambda', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

    role_name = 'GreenLambdaBenchmarkRole'
    
    try:
        role = iam_client.get_role(RoleName=role_name)
        role_arn = role['Role']['Arn']
        print(f"[SUCCESS] Found existing IAM role: {role_arn}")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"[NOTE] IAM Role '{role_name}' not found. Creating it now...")
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
        print("Role created. Waiting 10 seconds for IAM propagation across AWS...")
        time.sleep(10)

    benchmark_dir = 'benchmarks'
    for filename in os.listdir(benchmark_dir):
        if filename.endswith('.py'):
            func_name = filename.replace('.py', '').replace('_', '-')
            file_path = os.path.join(benchmark_dir, filename)
            
            zip_path = os.path.join(benchmark_dir, f"{func_name}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(file_path, arcname=filename)
                
            with open(zip_path, 'rb') as f:
                zipped_code = f.read()

            print(f"Deploying/Updating AWS Lambda: {func_name} ...")
            try:
                lambda_client.create_function(
                    FunctionName=func_name,
                    Runtime='python3.11',
                    Role=role_arn,
                    Handler=f"{filename.replace('.py', '')}.lambda_handler",
                    Code={'ZipFile': zipped_code},
                    Timeout=15,
                    MemorySize=128
                )
                print(f"   [SUCCESS] Created new {func_name} (Python 3.11).")
            except lambda_client.exceptions.ResourceConflictException:
                lambda_client.update_function_code(FunctionName=func_name, ZipFile=zipped_code)
                try:
                    # Upgrade the environment config ensuring it's 3.11
                    lambda_client.update_function_configuration(FunctionName=func_name, Runtime='python3.11')
                    print(f"   [SUCCESS] Updated {func_name} Code & Runtime to Python 3.11.")
                except Exception as config_err:
                    print(f"   [WARNING] Code updated, but Runtime update failed: {str(config_err)}")
            except Exception as e:
                print(f"   [ERROR] Failed to deploy {func_name}: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python deploy_benchmarks.py <ACCESS_KEY> <SECRET_KEY> <REGION>")
        sys.exit(1)
    deploy_lambdas(sys.argv[1], sys.argv[2], sys.argv[3])
