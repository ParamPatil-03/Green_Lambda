import os
import sys
import json
import time
import argparse
import boto3
from botocore.exceptions import ClientError

# Configuration Constants
INVOCATIONS_PER_FUNCTION = 20
DELAY_BETWEEN_INVOCATIONS = 2  # seconds
DELAY_BETWEEN_FUNCTIONS = 5    # seconds
CLOUDWATCH_SETTLE_TIME = 90    # seconds
TEST_PAYLOAD = {"test": True, "v": 42}

# Function names matching AWS deployed format (using hyphens instead of underscores)
FUNCTION_NAMES = [
    "lambda-01-hello",
    "lambda-02-math-heavy",
    "lambda-03-high-complexity",
    "lambda-04-memory-hog",
    "lambda-05-deep-recursion",
    "lambda-06-string-ops",
    "lambda-07-io-simulated",
    "lambda-08-bloated-code",
    "lambda-09-sorting-alg",
    "lambda-10-json-parsing",
    "lambda-11-list-comprehension",
    "lambda-12-prime-numbers",
    "lambda-13-string-reversal",
    "lambda-14-dict-operations",
    "lambda-15-exception-testing",
    "lambda-16-nested-loops",
    "lambda-17-datetime-ops",
    "lambda-18-set-intersection",
    "lambda-19-tuple-unpacking",
    "lambda-20-basic-class",
    "lambda-21-bitwise-ops",
    "lambda-22-random-password",
    "lambda-23-palindrome-check",
    "lambda-24-counter-collection",
    "lambda-25-math-trig"
]

def load_credentials():
    """Load credentials from environment variables or fallback to aws_session.json."""
    # 1. Check environment variables
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
    
    if access_key and secret_key and region:
        return access_key, secret_key, region, "Environment Variables"

    # 2. Check local JSON file
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aws_session.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ak = data.get("accessKeyId")
            sk = data.get("secretAccessKey")
            rg = data.get("region")
            if ak and sk and rg:
                return ak, sk, rg, f"aws_session.json ({json_path})"
        except Exception as e:
            print(f"[WARNING] Failed to parse {json_path}: {e}")

    # No credentials found
    return None, None, None, None

def print_progress_bar(completed, total, failed_count=0):
    """Print a simple ASCII progress bar."""
    percent = (completed / total) * 100
    bar_length = 20
    filled_length = int(bar_length * completed // total)
    bar = '#' * filled_length + '.' * (bar_length - filled_length)
    sys.stdout.write(f"\rProgress: [{completed}/{total} functions complete] [{bar}] {percent:.1f}% (Failed functions: {failed_count})")
    sys.stdout.flush()

def main():
    parser = argparse.ArgumentParser(description="Green Lambda - Benchmark Invocation Script")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them")
    args = parser.parse_args()

    # Load credentials
    access_key, secret_key, region, source = load_credentials()
    
    # Estimate time
    total_funcs = len(FUNCTION_NAMES)
    total_invocations = total_funcs * INVOCATIONS_PER_FUNCTION
    time_per_func = (INVOCATIONS_PER_FUNCTION * DELAY_BETWEEN_INVOCATIONS) + DELAY_BETWEEN_FUNCTIONS
    est_seconds = (total_funcs * time_per_func) + CLOUDWATCH_SETTLE_TIME
    est_minutes = est_seconds / 60.0

    print("Green Lambda -- Benchmark Invocation Script")
    print("==========================================")
    print(f"Functions to invoke: {total_funcs}")
    print(f"Invocations per function: {INVOCATIONS_PER_FUNCTION}")
    print(f"Total invocations: {total_invocations}")
    print(f"Estimated time: ~{est_minutes:.2f} minutes")
    
    if not access_key or not secret_key or not region:
        print("\n[ERROR] AWS Credentials could not be loaded!")
        print("Please configure environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)")
        print("or create a session config file at '/backend/aws_session.json'.")
        sys.exit(1)

    print(f"AWS Region: {region}")
    print(f"Credentials source: {source}")
    
    if args.dry_run:
        print("\n*** DRY RUN MODE ENABLED ***")
        print("Function list to be invoked (20 times each):")
        for idx, fn in enumerate(FUNCTION_NAMES, 1):
            print(f"  {idx:02d}. {fn}")
        print("\nDry run completed successfully. Setup is valid.")
        sys.exit(0)

    # Initialize boto3 lambda client
    try:
        lambda_client = boto3.client(
            "lambda",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        # Test credentials validity with a lightweight API call
        lambda_client.list_functions(MaxItems=1)
    except Exception as e:
        print(f"\n[ERROR] AWS Authentication Failed: {e}")
        sys.exit(1)

    print("\nStarting in 3 seconds... (Ctrl+C to cancel)")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\nStarting benchmark invocation process...\n")

    summary_results = []
    completed_funcs = 0
    failed_funcs = 0

    for fn in FUNCTION_NAMES:
        print(f"\n>>> Invoking {fn} (0/{INVOCATIONS_PER_FUNCTION})...")
        success_count = 0
        fail_count = 0
        skip_fn = False

        # Try to invoke once to see if function exists
        try:
            res = lambda_client.invoke(
                FunctionName=fn,
                InvocationType='RequestResponse',
                Payload=json.dumps(TEST_PAYLOAD)
            )
            status = res.get('StatusCode')
            if status == 200:
                success_count += 1
                print(f"  [1/{INVOCATIONS_PER_FUNCTION}] Success -- duration tracked")
            else:
                fail_count += 1
                print(f"  [1/{INVOCATIONS_PER_FUNCTION}] Error: Bad Status Code {status}")
        except ClientError as ce:
            err_code = ce.response.get('Error', {}).get('Code')
            if err_code == 'ResourceNotFoundException':
                print(f"  [WARNING] Function {fn} not found on AWS Lambda. Skipping...")
                skip_fn = True
            else:
                fail_count += 1
                print(f"  [1/{INVOCATIONS_PER_FUNCTION}] Error: {ce}")
        except Exception as e:
            fail_count += 1
            print(f"  [1/{INVOCATIONS_PER_FUNCTION}] Error: {e}")

        if skip_fn:
            summary_results.append((fn, 0, 0, 0, "SKIPPED"))
            failed_funcs += 1
            continue

        # Complete the rest of the 19 invocations
        for n in range(2, INVOCATIONS_PER_FUNCTION + 1):
            time.sleep(DELAY_BETWEEN_INVOCATIONS)
            try:
                res = lambda_client.invoke(
                    FunctionName=fn,
                    InvocationType='RequestResponse',
                    Payload=json.dumps(TEST_PAYLOAD)
                )
                status = res.get('StatusCode')
                if status == 200:
                    success_count += 1
                    print(f"  [{n}/{INVOCATIONS_PER_FUNCTION}] Success -- duration tracked")
                else:
                    fail_count += 1
                    print(f"  [{n}/{INVOCATIONS_PER_FUNCTION}] Error: Bad Status Code {status}")
            except Exception as e:
                fail_count += 1
                print(f"  [{n}/{INVOCATIONS_PER_FUNCTION}] Error: {e}")

        print(f"Completed: {fn} -- {success_count} success, {fail_count} failed")
        
        summary_results.append((fn, INVOCATIONS_PER_FUNCTION, success_count, fail_count, "OK"))
        completed_funcs += 1
        
        # Print progress bar
        print_progress_bar(completed_funcs, total_funcs, failed_funcs)
        print() # New line after progress bar

        # Settle delay between different functions
        time.sleep(DELAY_BETWEEN_FUNCTIONS)

    # 4. Print Summary Table
    print("\n======= INVOCATION SUMMARY =======")
    print(f"{'Function Name':<30} | {'Total Runs':<10} | {'Success':<8} | {'Failed':<8} | {'Status':<10}")
    print("-" * 75)
    
    total_runs_all = 0
    total_success_all = 0
    total_failed_all = 0
    
    for row in summary_results:
        fn, runs, ok, err, st = row
        print(f"{fn:<30} | {runs:<10} | {ok:<8} | {err:<8} | {st:<10}")
        total_runs_all += runs
        total_success_all += ok
        total_failed_all += err

    print("-" * 75)
    print(f"{'TOTALS':<30} | {total_runs_all:<10} | {total_success_all:<8} | {total_failed_all:<8} |")
    print("==================================\n")

    # 5. Settle Countdown
    print(f"Waiting {CLOUDWATCH_SETTLE_TIME} seconds for CloudWatch metrics to populate...")
    settle_remaining = CLOUDWATCH_SETTLE_TIME
    while settle_remaining > 0:
        print(f"CloudWatch settling... {settle_remaining}s remaining")
        time.sleep(10)
        settle_remaining -= 10

    print("\nAll done! CloudWatch metrics are ready.")
    print("You can now open Green Lambda and collect runtime metrics")
    print("for each function -- all 25 will have clean stable data.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Script execution cancelled by user.")
        sys.exit(0)
