import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, prepare_features, fn_lookup

def run_tests():
    print(f"Total unique functions in dataset lookup: {fn_lookup['function_name'].nunique()}")
    
    test_functions = [
        "etl-transform-10",       # Expansion ETL
        "image-proc-10",          # Expansion Data Processing
        "ml-inference-05",        # Expansion Compute Heavy
        "fake-unknown-function"   # Should trigger fallback
    ]
    
    client = app.test_client()
    
    for fn in test_functions:
        print(f"\n--- Testing {fn} ---")
        
        # Test prepare_features directly to see the loaded values
        X_single, row_details, is_fallback = prepare_features(fn)
        
        print(f"Is Fallback: {is_fallback}")
        
        if not is_fallback:
            print(f"Loaded Memory MB: {row_details['memory_config_mb'].values[0]}")
            print(f"Loaded Duration MS: {row_details['aws_duration_ms'].values[0]}")
            print(f"Loaded LOC: {row_details['lines_of_code'].values[0]}")
            
        # Test the API endpoint directly
        payload = {
            "functionName": fn,
            "model": "xgboost",
            "baselineRph": 10000
        }
        response = client.post('/analyze-function', json=payload)
        data = json.loads(response.data)
        
        if 'error' in data:
            print(f"Error from API: {data['error']}")
        else:
            print(f"API Confidence: {data['confidence']}")
            print(f"API Energy Wh/invocation: {data['energyWhPerInvocation']}")

if __name__ == "__main__":
    run_tests()
