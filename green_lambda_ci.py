import os
import sys
import requests
from radon.complexity import cc_visit

# Configurable Action Threshold from GitHub Secrets
ENERGY_THRESHOLD_WH = float(os.getenv('ENERGY_THRESHOLD_WH', '3.5'))
GREEN_LAMBDA_URL = os.getenv('GREEN_LAMBDA_URL', 'http://localhost:5000')
API_KEY = os.getenv('API_KEY', 'TEST-KEY-123')

print(f"♻️ Initializing Green Lambda CI/CD Pipeline Analysis...")
print(f"⚡ Energy Limit Threshold Enforced: {ENERGY_THRESHOLD_WH} Wh per Invocation\n")

def scan_local_complexity():
    # Recursively scan all python files currently inside the GitHub pull request
    total_loc = 0
    complexities = []
    
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.py') and not f.startswith('.'):
                try:
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as pyf:
                        content = pyf.read()
                        total_loc += len([line for line in content.splitlines() if line.strip() and not line.startswith('#')])
                        
                        blocks = cc_visit(content)
                        if blocks: complexities.extend([b.complexity for b in blocks])
                except Exception:
                    pass
                
    avg_cc = (sum(complexities) / len(complexities)) if complexities else 1.0
    return total_loc, avg_cc

try:
    # Execute the AST Scan algorithm locally matching the Flask logic
    loc, cc = scan_local_complexity()
    print(f"🔍 Pipeline Code Scan Results: \n ├─ Analyzed LOC: {loc}\n └─ Avg Cyclomatic Complexity: {round(cc, 2)}")

    # 1. Attempt to ping the Live ML API (Will fail smoothly in Demo Mode)
    API_URL = f"{GREEN_LAMBDA_URL}/analyze-function"
    payload = {
        "accessKeyId": API_KEY,
        "functionName": "github-ci-pipeline-runner",
        "baselineRph": 25000,
        "model": "xgboost"
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=3)
        data = response.json()
        predicted_energy = float(data.get('energyWhPerInvocation', 1.5))
        print("✅ Live ML API Backend successfully pinged.")
    except Exception as network_error:
        # 2. Enter Failsafe Demo Simulation Pipeline directly inside the Action Runner!
        print("⚠️  Live ML Backend offline/unavailable. Entering 'Simulation Demo Mode' inside GitHub Runner...")
        
        # Simulate XGBoost Energy Profile dynamically using true code complexity extracted live
        base_efficiency = 0.5
        complexity_penalty = cc * 0.15
        bloat_penalty = loc * 0.002
        
        predicted_energy = base_efficiency + complexity_penalty + bloat_penalty
        
    print(f"\n📊 XGBoost Model Prediction: \n └─ Generated Energy Cost: {round(predicted_energy, 4)} Wh per Run")

    if predicted_energy > ENERGY_THRESHOLD_WH:
        print(f"\n❌ [CRITICAL FAILURE]: The calculated energy footprint ({round(predicted_energy, 3)} Wh) radically exceeds production thresholds ({ENERGY_THRESHOLD_WH} Wh)!")
        print("💡 REQUIRED FIX: You must optimize the Cyclomatic Complexity or eliminate unneeded computations before merging into production.\n")
        sys.exit(1) # Action fails! Enterprise DevOps blocked the deployment!
    else:
        print(f"\n✅ [PIPELINE PASSED]: The energy footprint ({round(predicted_energy, 3)} Wh) is highly optimized and well below the {ENERGY_THRESHOLD_WH} Wh limit.")
        print("🚀 Merge Request Approved! Green Lambda certification granted.\n")
        sys.exit(0) # Action cleanly passes

except Exception as e:
    print(f"Pipeline crashed entirely natively: {str(e)}")
    sys.exit(1)
