import os
import zipfile

# Create the folder
bench_dir = 'benchmarks_v2'
os.makedirs(bench_dir, exist_ok=True)

print("="*60)
print("GENERATING 150 NEW BENCHMARK FUNCTIONS (V2)")
print("Including calibrated multi-second and 20-60s durations")
print("="*60)

# Category 1: REST API (30 functions)
for i in range(1, 31):
    func_name = f"rest_api_{i:02d}"
    iterations = i * 100
    user_count = i * 10
    post_count = i * 5
    comment_count = i * 8
    
    # We will add a duration control loop for variants 25-30
    target_duration = 0.0
    if i >= 25:
        iterations = i * 3000
        # target durations: 25 -> 20s, 26 -> 28s, 27 -> 36s, 28 -> 44s, 29 -> 52s, 30 -> 60s
        target_duration = 20.0 + (i - 25) * 8.0
        
    code = f"""import json
import hashlib
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        iterations = {iterations}
        headers = event.get('headers', {{}}) or {{}}
        query_params = event.get('queryStringParameters', {{}}) or {{}}
        
        token = headers.get('Authorization', 'Bearer dummy-token-{i}')
        h = hashlib.sha256()
        
        # Heavy computation
        for j in range(iterations):
            h.update(f"{{token}}-{{j}}".encode('utf-8'))
        token_hash = h.hexdigest()
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < {target_duration}:
            h.update(b"additional-busy-wait-cycles")
            token_hash = h.hexdigest()
            
        route = query_params.get('route', 'default')
        if route == 'users':
            data = {{"status": "ok", "users": [f"user_{{x}}" for x in range({user_count})]}}
        elif route == 'posts' and {i} % 2 == 0:
            data = {{"status": "ok", "posts": [f"post_{{x}}" for x in range({post_count})]}}
        elif route == 'comments' and {i} % 3 == 0:
            data = {{"status": "ok", "comments": [f"comment_{{x}}" for x in range({comment_count})]}}
        else:
            data = {{"status": "ok", "message": "Welcome to REST API {i:02d}!"}}
            
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'api': '{func_name}',
                'hash': token_hash,
                'data': data
            }})
        }}
    except Exception as e:
        return {{'statusCode': 500, 'body': str(e)}}
"""
    with open(os.path.join(bench_dir, f"{func_name}.py"), 'w', encoding='utf-8') as f:
        f.write(code)

# Category 2: ETL / Data Transform (30 functions)
for i in range(1, 31):
    func_name = f"etl_transform_{i:02d}"
    row_count = i * 250
    modulo_val = max(2, i // 2)
    
    target_duration = 0.0
    if i >= 25:
        row_count = i * 8000
        target_duration = 20.0 + (i - 25) * 8.0
        
    code = f"""import json
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        rows = []
        for r in range({row_count}):
            rows.append({{
                'id': r,
                'category': f"cat_{{r % {modulo_val}}}",
                'value': float(r * 1.5),
                'active': (r % 2 == 0)
            }})
            
        transformed = []
        aggregates = {{}}
        for row in rows:
            if row['active']:
                new_val = (row['value'] * 1.12) / 0.95
                transformed.append({{
                    'id': row['id'],
                    'cat': row['category'].upper(),
                    'val': new_val
                }})
                cat = row['category']
                aggregates[cat] = aggregates.get(cat, 0.0) + new_val
                
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < {target_duration}:
            # Simulating additional ETL transformations
            for row in rows[:1000]:
                dummy = (row['value'] * 1.05) / 0.99
                
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'etl': '{func_name}',
                'processed_rows': len(rows),
                'transformed_rows': len(transformed),
                'category_totals': aggregates
            }})
        }}
    except Exception as e:
        return {{'statusCode': 500, 'body': str(e)}}
"""
    with open(os.path.join(bench_dir, f"{func_name}.py"), 'w', encoding='utf-8') as f:
        f.write(code)

# Category 3: Image Processing (30 functions)
for i in range(1, 31):
    func_name = f"image_proc_{i:02d}"
    dim = i * 12
    filter_loops = 1
    
    target_duration = 0.0
    if i >= 25:
        dim = i * 20
        filter_loops = 10
        target_duration = 20.0 + (i - 25) * 8.0
        
    code = f"""import json
import math
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        pixels = [[float((r * c) % 256) for c in range({dim})] for r in range({dim})]
        
        filtered = [[0.0 for _ in range({dim})] for _ in range({dim})]
        kernel_sum = 0.0
        
        for loop in range({filter_loops}):
            for r in range(1, {dim} - 1):
                for c in range(1, {dim} - 1):
                    val = (
                        pixels[r-1][c-1] + pixels[r-1][c] + pixels[r-1][c+1] +
                        pixels[r][c-1]   + pixels[r][c]   + pixels[r][c+1] +
                        pixels[r+1][c-1] + pixels[r+1][c] + pixels[r+1][c+1]
                    ) / 9.0
                    filtered[r][c] = val
                    if loop == {filter_loops - 1}:
                        kernel_sum += val
                        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < {target_duration}:
            # Simulating additional pixel manipulation runs
            dummy_sum = sum(filtered[0])
            
        resized = []
        for r in range(0, {dim}, 2):
            row = []
            for c in range(0, {dim}, 2):
                row.append(filtered[r][c])
            resized.append(row)
            
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'image': '{func_name}',
                'original_dim': '{dim}x{dim}',
                'resized_dim': f"{{len(resized)}}x{{len(resized[0]) if resized else 0}}",
                'pixel_sum': kernel_sum
            }})
        }}
    except Exception as e:
        return {{'statusCode': 500, 'body': str(e)}}
"""
    with open(os.path.join(bench_dir, f"{func_name}.py"), 'w', encoding='utf-8') as f:
        f.write(code)

# Category 4: ML Inference (30 functions)
for i in range(1, 31):
    func_name = f"ml_inference_{i:02d}"
    features_count = i * 5
    
    target_duration = 0.0
    if i >= 25:
        features_count = i * 40
        target_duration = 20.0 + (i - 25) * 8.0
        
    code = f"""import json
import math
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        x_vec = [float((idx * 1.7) % 5.0) for idx in range({features_count})]
        
        classes = ['Green', 'Amber', 'Red']
        scores = {{c: 0.0 for c in classes}}
        
        for c in classes:
            prior = 0.33
            score = math.log(prior)
            for f_idx, val in enumerate(x_vec):
                mean = float((f_idx * 1.1) % 4.0)
                var = 1.0 + float((f_idx * 0.2) % 2.0)
                likelihood = (1.0 / math.sqrt(2.0 * math.pi * var)) * math.exp(-((val - mean) ** 2) / (2.0 * var))
                score += math.log(max(1e-9, likelihood))
            scores[c] = score
            
        predicted_class = max(scores, key=scores.get)
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < {target_duration}:
            # Simulating additional classifier steps
            dummy_calc = math.sin(x_vec[0]) * math.cos(x_vec[-1])
            
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'ml': '{func_name}',
                'features_count': len(x_vec),
                'prediction': predicted_class,
                'scores': scores
            }})
        }}
    except Exception as e:
        return {{'statusCode': 500, 'body': str(e)}}
"""
    with open(os.path.join(bench_dir, f"{func_name}.py"), 'w', encoding='utf-8') as f:
        f.write(code)

# Category 5: Scientific Computing (30 functions)
for i in range(1, 31):
    func_name = f"scientific_calc_{i:02d}"
    iterations = i * 2000
    intervals = i * 100
    
    target_duration = 0.0
    if i >= 25:
        iterations = i * 40000
        target_duration = 20.0 + (i - 25) * 8.0
        
    code = f"""import json
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        inside = 0
        total = {iterations}
        
        state = 42
        for step in range(total):
            state = (state * 1103515245 + 12345) & 0x7fffffff
            x = state / 2147483647.0
            state = (state * 1103515245 + 12345) & 0x7fffffff
            y = state / 2147483647.0
            
            if x*x + y*y <= 1.0:
                inside += 1
                
        pi_estimate = 4.0 * inside / total
        
        n_intervals = {intervals}
        dx = 10.0 / n_intervals
        integral_sum = 0.5 * (0.0 + 100.0)
        for step in range(1, n_intervals):
            x_val = step * dx
            integral_sum += x_val * x_val
        integral_sum *= dx
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < {target_duration}:
            # Simulating busy loops
            state = (state * 1103515245 + 12345) & 0x7fffffff
            
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'scientific': '{func_name}',
                'pi_estimate': pi_estimate,
                'integral': integral_sum,
                'iterations': total
            }})
        }}
    except Exception as e:
        return {{'statusCode': 500, 'body': str(e)}}
"""
    with open(os.path.join(bench_dir, f"{func_name}.py"), 'w', encoding='utf-8') as f:
        f.write(code)

print("[*] All 150 python benchmark files successfully written.")

# Zip all generated files
print("Zipping benchmark files...")
for filename in os.listdir(bench_dir):
    if filename.endswith('.py'):
        file_path = os.path.join(bench_dir, filename)
        zip_path = os.path.join(bench_dir, filename.replace('.py', '.zip'))
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(file_path, arcname=filename)

print("[*] Zipped 150 benchmark files successfully.")
print("="*60)
