import boto3
import time
import sys

def fix_runtimes(access_key, secret_key, region):
    lambda_client = boto3.client('lambda', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
    for i in range(1, 11):
        func_name = f"lambda-{str(i).zfill(2)}-"
        # Find exact name
        try:
            paginator = lambda_client.get_paginator('list_functions')
            foos = []
            for page in paginator.paginate():
                for f in page['Functions']:
                    if f['FunctionName'].startswith(func_name):
                        foos.append(f['FunctionName'])
            for f_name in foos:
                state = lambda_client.get_function(FunctionName=f_name)['Configuration']['LastUpdateStatus']
                while state == 'InProgress':
                    print(f"Waiting for {f_name} to finish update...")
                    time.sleep(2)
                    state = lambda_client.get_function(FunctionName=f_name)['Configuration']['LastUpdateStatus']
                
                print(f"Updating configuration for {f_name} to python3.11...")
                lambda_client.update_function_configuration(FunctionName=f_name, Runtime='python3.11')
        except Exception as e:
            print(f"Error on {func_name}: {e}")

if __name__ == "__main__":
    fix_runtimes(sys.argv[1], sys.argv[2], sys.argv[3])
