import os

os.makedirs('benchmarks', exist_ok=True)

# Define the rewritten 25 Lambda functions with different complexity and resource footprints
lambdas = {
    "lambda_01_hello.py": '''import os
import datetime

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Returns basic system and region metadata.
    Expected duration: <100ms, Expected memory: <5MB
    """
    try:
        region = os.environ.get('AWS_REGION', 'us-east-1')
        timestamp = datetime.datetime.now().isoformat()
        res = f"Hello from Green Lambda! Region: {region}, Timestamp: {timestamp}, Status: ACTIVE"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_02_math_heavy.py": '''import math

def get_cofactor(matrix, i, j):
    res = []
    for r in range(len(matrix)):
        if r != i:
            row = []
            for c in range(len(matrix[r])):
                if c != j:
                    row.append(matrix[r][c])
            res.append(row)
    return res

def get_determinant(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0
    sign = 1
    for j in range(n):
        cof = get_cofactor(matrix, 0, j)
        det += sign * matrix[0][j] * get_determinant(cof)
        sign = -sign
    return det

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Computes cofactor expansion determinant and factorial series.
    Expected duration: 3000-4000ms, Expected memory: <20MB
    """
    try:
        # Run cofactor expansion determinant on multiple 5x5 matrices to burn CPU
        total = 0.0
        matrix = [
            [3.1, 2.4, 5.6, 0.8, 1.2],
            [0.5, 4.2, 1.7, 9.3, 2.1],
            [1.2, 0.9, 8.5, 4.4, 3.3],
            [5.5, 1.1, 0.2, 7.8, 6.9],
            [2.2, 3.3, 4.4, 5.5, 0.1]
        ]
        # Run it 600 times to scale execution time
        for i in range(600):
            det = get_determinant(matrix)
            # Slightly perturb matrix to avoid CPU caching optimizations
            matrix[0][0] = (matrix[0][0] + 0.0001) % 10.0
            total += det
        
        # Burn a bit more CPU with floating-point expansions
        val = 0.0
        for x in range(1, 20000):
            val += math.sqrt(x) * math.log(x)
            
        return {'statusCode': 200, 'body': f"Determinant sum: {total:.4f}, Val: {val:.4f}"}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_03_high_complexity.py": '''def classify_point(x, y, z, w, v):
    # Deep nesting with if/elif/else to generate high cyclomatic complexity
    if x > 0.5:
        if y < 0.3:
            if z > 0.7:
                if w == 'A':
                    if v % 2 == 0:
                        return 1
                    else:
                        return 2
                else:
                    return 3
            else:
                if w == 'B':
                    return 4
                else:
                    return 5
        else:
            if z < 0.4:
                if w == 'A':
                    return 6
                else:
                    return 7
            else:
                return 8
    else:
        if y > 0.6:
            if z < 0.2:
                if w == 'C':
                    return 9
                else:
                    return 10
            else:
                if w == 'A':
                    return 11
                else:
                    return 12
        else:
            if z > 0.5:
                if v % 3 == 0:
                    return 13
                else:
                    return 14
            else:
                return 15

def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Pure Python Decision Tree Classifier.
    Expected duration: 1500-2500ms, Expected memory: 15-35MB
    """
    try:
        # Classify 12,000 synthetic data points to consume CPU time
        counts = [0] * 16
        for i in range(12000):
            x = (i * 17 % 100) / 100.0
            y = (i * 23 % 100) / 100.0
            z = (i * 31 % 100) / 100.0
            w = ['A', 'B', 'C', 'D'][i % 4]
            v = i
            cls = classify_point(x, y, z, w, v)
            counts[cls] += 1
            
        res = f"Class counts: {counts}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_04_memory_hog.py": '''def lambda_handler(event, context):
    """Category 3: Memory Heavy. Allocates large lists and dictionaries to stress memory.
    Expected duration: 800-1500ms, Expected memory: 60-80MB
    """
    try:
        # 1. Allocate large lists
        str_list = [f"MemoryHogDataElement_{i}" for i in range(400000)]
        
        # 2. Dictionary with 80,000 key-value pairs
        data_dict = {f"key_{i}": f"value_{i*2}" for i in range(80000)}
        
        # 3. Tuple structures
        tuples_list = [(i, i+1, i+2, i+3, i+4, i+5, i+6, i+7, i+8, i+9) for i in range(10000)]
        
        # Access elements to verify allocation and prevent optimization garbage collection
        str_checksum = sum(1 for s in str_list if len(s) > 20)
        dict_checksum = sum(1 for k in data_dict if k.startswith("key_5"))
        tuple_sum = sum(t[5] for t in tuples_list)
        
        res = f"Allocated structures. Checksums: str_list={str_checksum}, dict={dict_checksum}, tuple_sum={tuple_sum}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_05_deep_recursion.py": '''import sys
sys.setrecursionlimit(10000)

class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert_bst(root, val):
    if root is None:
        return BSTNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root

def inorder_traverse(root, result):
    if root:
        inorder_traverse(root.left, result)
        result.append(root.val)
        inorder_traverse(root.right, result)

def merge_sort_rec(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_rec(arr[:mid])
    right = merge_sort_rec(arr[mid:])
    
    # Merge step
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

def binary_search_rec(arr, low, high, x):
    if high >= low:
        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search_rec(arr, low, mid - 1, x)
        else:
            return binary_search_rec(arr, mid + 1, high, x)
    return -1

def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Recursive sorting, binary search, and BST traversal.
    Expected duration: 1500-2500ms, Expected memory: 15-35MB
    """
    try:
        total_sorted_len = 0
        search_hits = 0
        bst_traversed_len = 0
        
        for iteration in range(25):
            arr = [(x * 123 % 5000) for x in range(2000)]
            sorted_arr = merge_sort_rec(arr)
            total_sorted_len += len(sorted_arr)
            
            for target in [100, 200, 300, 400, 500]:
                idx = binary_search_rec(sorted_arr, 0, len(sorted_arr) - 1, target)
                if idx != -1:
                    search_hits += 1
                    if target % 200 == 0:
                        search_hits += 10
                    elif target % 300 == 0:
                        search_hits += 5
                    else:
                        search_hits += 1
                else:
                    if target > 300:
                        search_hits -= 1
                        
            if iteration < 3:
                root = None
                for val in sorted_arr[:300]:
                    if val % 2 == 0:
                        root = insert_bst(root, val)
                    else:
                        root = insert_bst(root, val + 1)
                bst_res = []
                inorder_traverse(root, bst_res)
                bst_traversed_len += len(bst_res)
                
        res = f"Sorted len: {total_sorted_len}, Search hits: {search_hits}, BST inorder: {bst_traversed_len}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_06_string_ops.py": '''def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Simple string operations.
    Expected duration: 100-300ms, Expected memory: <5MB
    """
    try:
        base = "GreenLambdaOptimizationBaseline" * 40
        upper_str = base.upper()
        lower_str = base.lower()
        replaced = base.replace("e", "3").replace("a", "4")
        substring = base[10:100]
        words_len = len(base.split("a"))
        
        res = f"Upper: {upper_str[:10]}, Lower: {lower_str[:10]}, Replaced: {replaced[:10]}, Sub: {substring}, SplitLen: {words_len}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_07_io_simulated.py": '''import json

def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Deep string serialization and JSON data manipulation.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        records = []
        for i in range(12000):
            # Simulate high depth dictionary record
            rec = {
                "id": i,
                "uuid": f"uuid_record_simulated_{i*13}",
                "active": i % 2 == 0,
                "score": float(i * 1.5),
                "tags": ["cloud", "lambda", "green", f"tag_{i%5}"],
                "metadata": {
                    "env": "production",
                    "region": "ap-south-1",
                    "latency_limit_ms": 150
                }
            }
            records.append(rec)
            
        # Serialize to huge string
        json_data = json.dumps(records)
        
        # Deserialize back
        loaded = json.loads(json_data)
        
        # Validate and edit fields
        valid_count = 0
        for item in loaded:
            if item["id"] >= 0 and "metadata" in item:
                item["score"] += 10.0
                item["metadata"]["env"] = "staging"
                valid_count += 1
                
        # Re-serialize
        final_str = json.dumps(loaded)
        
        res = f"Processed {len(loaded)} records. Valid: {valid_count}, FinalSize: {len(final_str)}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_08_bloated_code.py": '''def lambda_handler(event, context):
    """Category 3: Memory Heavy. Matrix operations on a large 2D list of float values.
    Expected duration: 1000-2000ms, Expected memory: 50-70MB
    """
    try:
        rows = 1000
        cols = 500
        # Build large 2D grid
        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                row.append(float(r * c * 0.001))
            grid.append(row)
            
        # Row sums
        row_sums = [sum(row) for row in grid]
        
        # Column sums (intensive loop)
        col_sums = [0.0] * cols
        for c in range(cols):
            c_sum = 0.0
            for r in range(rows):
                c_sum += grid[r][c]
            col_sums[c] = c_sum
            
        # Find min and max
        min_val = grid[0][0]
        max_val = grid[0][0]
        for row in grid:
            for val in row:
                if val < min_val:
                    min_val = val
                elif val > max_val:
                    max_val = val
                    
        res = f"Grid processed: min={min_val:.3f}, max={max_val:.3f}, sum_row0={row_sums[0]:.3f}, sum_col0={col_sums[0]:.3f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_09_sorting_alg.py": '''import random
import time

def bubble_sort(arr):
    n = len(arr)
    res = list(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if res[j] > res[j + 1]:
                res[j], res[j + 1] = res[j + 1], res[j]
    return res

def insertion_sort(arr):
    res = list(arr)
    for i in range(1, len(res)):
        key = res[i]
        j = i - 1
        while j >= 0 and key < res[j]:
            res[j + 1] = res[j]
            j -= 1
        res[j + 1] = key
    return res

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Performance comparison of 4 sorting algorithms.
    Expected duration: 2000-3000ms, Expected memory: 15-35MB
    """
    try:
        # Sort 1,000 elements for slower Bubble and Insertion sorting
        base_arr = [random.randint(1, 10000) for _ in range(1000)]
        
        t0 = time.perf_counter()
        _ = bubble_sort(base_arr)
        t_bubble = time.perf_counter() - t0
        
        t0 = time.perf_counter()
        _ = insertion_sort(base_arr)
        t_insert = time.perf_counter() - t0
        
        # Scale list to 2,000 for faster Merge and Quick sort
        extended_arr = base_arr + [random.randint(1, 10000) for _ in range(1000)]
        
        t0 = time.perf_counter()
        _ = merge_sort(extended_arr)
        t_merge = time.perf_counter() - t0
        
        t0 = time.perf_counter()
        _ = quick_sort(extended_arr)
        t_quick = time.perf_counter() - t0
        
        res = f"Timings: Bubble={t_bubble:.4f}s, Insertion={t_insert:.4f}s, Merge={t_merge:.4f}s, Quick={t_quick:.4f}s"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_10_json_parsing.py": '''import json

def build_nested_structure(depth, width):
    if depth == 0:
        return {"value": 1.5, "flag": True, "label": "leaf"}
    res = {}
    for i in range(width):
        res[f"key_{i}"] = build_nested_structure(depth - 1, width)
    return res

def collect_values(obj, results):
    if isinstance(obj, dict):
        if "value" in obj:
            results.append(obj["value"])
        for k, v in obj.items():
            if k != "value":
                collect_values(v, results)
    elif isinstance(obj, list):
        for item in obj:
            collect_values(item, results)

def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Nested JSON generation, parsing, and traversal.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        # Build nested data tree (depth=4, width=8 gives 8^4 = 4096 leaves)
        tree = build_nested_structure(4, 8)
        
        # Serialize
        serialized = json.dumps(tree)
        
        # Deserialize
        deserialized = json.loads(serialized)
        
        # Collect values recursively
        values = []
        collect_values(deserialized, values)
        
        # Compute stats
        v_sum = sum(values)
        v_avg = v_sum / len(values) if values else 0.0
        
        res = f"Traversed nested JSON. Leaves count: {len(values)}, Sum: {v_sum:.2f}, Avg: {v_avg:.2f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_11_list_comprehension.py": '''import time

def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. List comprehensions vs for-loops benchmark.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        # 1. Benchmark comprehensions
        t0 = time.perf_counter()
        nums = [x for x in range(300000)]
        evens_squared = [n * n for n in nums if n % 2 == 0 and n % 3 == 0]
        
        # Nested comprehension
        matrix = [[x * y for x in range(10)] for y in range(1000)]
        flattened = [val for row in matrix for val in row]
        t_comp = time.perf_counter() - t0
        
        # 2. Benchmark equivalent for-loops
        t1 = time.perf_counter()
        loop_nums = []
        for x in range(300000):
            loop_nums.append(x)
        
        loop_evens_squared = []
        for n in loop_nums:
            if n % 2 == 0:
                if n % 3 == 0:
                    loop_evens_squared.append(n * n)
                    
        loop_matrix = []
        for y in range(1000):
            row = []
            for x in range(10):
                row.append(x * y)
            loop_matrix.append(row)
            
        loop_flattened = []
        for row in loop_matrix:
            for val in row:
                loop_flattened.append(val)
        t_loop = time.perf_counter() - t1
        
        res = f"List comp: {t_comp:.4f}s (len={len(evens_squared)}, flat={len(flattened)}), For-loop: {t_loop:.4f}s"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_12_prime_numbers.py": '''def sieve_of_eratosthenes(limit):
    primes = [True] * (limit + 1)
    primes[0] = primes[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if primes[i]:
            for j in range(i*i, limit + 1, i):
                primes[j] = False
    return [i for i, is_prime in enumerate(primes) if is_prime]

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Generating primes using Sieve and finding twin primes.
    Expected duration: 2000-3000ms, Expected memory: <20MB
    """
    try:
        limit = 50000
        # Run multiple times to occupy CPU
        all_primes = []
        for _ in range(20):
            all_primes = sieve_of_eratosthenes(limit)
            
        # Twin primes
        twin_primes = []
        for i in range(len(all_primes) - 1):
            if all_primes[i+1] - all_primes[i] == 2:
                twin_primes.append((all_primes[i], all_primes[i+1]))
                
        # Prime pairs summation
        pair_sum = sum(p1 + p2 for p1, p2 in twin_primes)
        
        res = f"Primes count: {len(all_primes)}, Twin primes count: {len(twin_primes)}, Sum: {pair_sum}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_13_string_reversal.py": '''def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Reversing strings and simple palindrome checks.
    Expected duration: 100-300ms, Expected memory: <5MB
    """
    try:
        s1 = "abcdefghijklmnopqrstuvwxyz" * 20
        s2 = "ReverseMeGreenLambda" * 20
        
        rev1 = s1[::-1]
        rev2 = s2[::-1]
        
        is_pal1 = s1 == rev1
        is_pal2 = s2 == rev2
        
        res = f"Rev1Prefix: {rev1[:10]}, Rev2Prefix: {rev2[:10]}, IsPal1: {is_pal1}, IsPal2: {is_pal2}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_14_dict_operations.py": '''def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Large dictionary manipulations and set operations.
    Expected duration: 1000-2000ms, Expected memory: 20-40MB
    """
    try:
        # Create dicts
        dict1 = {f"key_{i}": f"val_{i % 100}" for i in range(50000)}
        dict2 = {f"key_{i}": f"val_{(i + 10) % 100}" for i in range(25000, 75000)}
        dict3 = {f"key_{i}": f"val_{i % 50}" for i in range(10000, 60000)}
        
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        keys3 = set(dict3.keys())
        
        # Intersections/Unions
        common_keys = keys1.intersection(keys2).intersection(keys3)
        all_keys = keys1.union(keys2).union(keys3)
        diff_keys = keys1.difference(keys2)
        
        # Build inverted index
        inverted = {}
        for k in common_keys:
            val = dict1[k]
            if val not in inverted:
                inverted[val] = []
            inverted[val].append(k)
            
        # Value frequency count
        val_counts = {v: len(keys) for v, keys in inverted.items()}
        sorted_counts = sorted(val_counts.items(), key=lambda x: x[1], reverse=True)
        
        res = f"Dict operations. CommonKeys: {len(common_keys)}, UnionKeys: {len(all_keys)}, DiffKeys: {len(diff_keys)}, TopFreq: {sorted_counts[:3]}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_15_exception_testing.py": '''def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Basic exception handling check.
    Expected duration: 50-200ms, Expected memory: <5MB
    """
    successes = 0
    failures = 0
    
    try:
        _ = 1 / 0
        successes += 1
    except ZeroDivisionError:
        failures += 1
        
    try:
        d = {}
        _ = d["missing"]
        successes += 1
    except KeyError:
        failures += 1
        
    try:
        _ = int("not_a_number")
        successes += 1
    except ValueError:
        failures += 1
        
    res = f"Exception tests. Success: {successes}, Failures: {failures}"
    return {'statusCode': 200, 'body': res}
''',

    "lambda_16_nested_loops.py": '''def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Deeply nested loops and multi-level calculations.
    Expected duration: 2000-3000ms, Expected memory: 15-35MB
    """
    try:
        dim_x = 50
        dim_y = 50
        dim_z = 10
        
        accumulator = 0.0
        for iteration in range(5):
            for x in range(dim_x):
                for y in range(dim_y):
                    for z in range(dim_z):
                        if (x + y + z) % 2 == 0:
                            for step in range(5):
                                val = (x * 0.1) + (y * 0.2) + (z * 0.3) + (step * 0.01)
                                if val > 15.0:
                                    if val < 20.0:
                                        accumulator += val * 1.5
                                    else:
                                        accumulator += val
                                else:
                                    if val > 5.0:
                                        accumulator -= val * 0.5
                                    else:
                                        accumulator -= val
                        else:
                            if x % 3 == 0:
                                accumulator += (x * y * z * 0.001)
                            else:
                                accumulator -= (x * y * z * 0.0005)
                                
        res = f"Deeply nested matrix calculation. Accumulator: {accumulator:.4f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_17_datetime_ops.py": '''import datetime

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Basic date computations.
    Expected duration: 200-400ms, Expected memory: <5MB
    """
    try:
        base_date = datetime.datetime(2023, 1, 1)
        dates = [base_date + datetime.timedelta(days=i*5) for i in range(10)]
        
        deltas = []
        for i in range(len(dates) - 1):
            delta = dates[i+1] - dates[i]
            deltas.append(delta.days)
            
        formatted = [d.strftime('%Y-%m-%d') for d in dates]
        
        res = f"First: {formatted[0]}, Last: {formatted[-1]}, Deltas: {deltas}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_18_set_intersection.py": '''def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Multi-set intersections and symmetric differences.
    Expected duration: 1000-2000ms, Expected memory: 20-40MB
    """
    try:
        # Generate 5 large sets with overlapping elements
        set1 = set(x * 2 % 200000 for x in range(100000))
        set2 = set(x * 3 % 200000 for x in range(100000))
        set3 = set(x * 5 % 200000 for x in range(100000))
        set4 = set(x * 7 % 200000 for x in range(100000))
        set5 = set(x * 11 % 200000 for x in range(100000))
        
        sets = [set1, set2, set3, set4, set5]
        
        # All pairwise intersections (10 pairs)
        pairwise_lens = []
        for i in range(5):
            for j in range(i + 1, 5):
                intersect = sets[i].intersection(sets[j])
                pairwise_lens.append(len(intersect))
                
        # Union
        union_set = set1.union(set2).union(set3).union(set4).union(set5)
        
        # Elements in exactly 3 of the 5 sets
        freq = {}
        for s in sets:
            for el in s:
                freq[el] = freq.get(el, 0) + 1
                
        count_exactly_3 = sum(1 for el, f in freq.items() if f == 3)
        
        res = f"Set operations: PairwiseIntersectionsAvg={sum(pairwise_lens)/len(pairwise_lens):.1f}, UnionSize={len(union_set)}, Exactly3SetsCount={count_exactly_3}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_19_tuple_unpacking.py": '''def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Heavy tuple unpacking, grouping, and sorting.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        # Generate 400,000 tuples of (id, value, category, score)
        data = []
        for i in range(400000):
            cat = f"cat_{i % 10}"
            score = float((i * 19 % 1000) / 10.0)
            data.append((i, f"data_val_{i}", cat, score))
            
        # Unpack and group by category
        groups = {}
        for item in data:
            idx, val, cat, score = item
            if cat not in groups:
                groups[cat] = []
            groups[cat].append((idx, score))
            
        # Sort each group by score and keep top 100
        top_scores = {}
        for cat, items in groups.items():
            items.sort(key=lambda x: x[1], reverse=True)
            top_scores[cat] = items[:100]
            
        # Compute average of top scores
        avg_top_scores = {}
        for cat, items in top_scores.items():
            avg_top_scores[cat] = sum(x[1] for x in items) / len(items)
            
        res = f"Processed {len(data)} tuples. Groups count: {len(groups)}, AvgTopScores: {list(avg_top_scores.items())[:3]}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_20_basic_class.py": '''class Node:
    __slots__ = ['val', 'next', 'prev']
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0
        
    def append(self, val):
        new_node = Node(val)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.count += 1
        
    def reverse(self):
        temp = None
        current = self.head
        self.tail = current
        while current is not None:
            temp = current.prev
            current.prev = current.next
            current.next = temp
            current = current.prev
        if temp is not None:
            self.head = temp.prev

def lambda_handler(event, context):
    """Category 3: Memory Heavy. Double-linked list instantiation, reversal, and searches.
    Expected duration: 1000-2000ms, Expected memory: 50-80MB
    """
    try:
        dll = DoublyLinkedList()
        # Build 100,000 node list with 50-character string payload to inflate memory usage
        payload_base = "GreenLambdaLinkedListPayloadNodeStringData50Chars_"
        for i in range(100000):
            dll.append(f"{payload_base}{i}")
            
        # Forward traversal
        curr = dll.head
        f_checksum = 0
        for _ in range(50000):
            if curr:
                f_checksum += len(curr.val)
                curr = curr.next
                
        # Reverse in place
        dll.reverse()
        
        # Traverse reversed list from head (original tail)
        curr = dll.head
        r_checksum = 0
        for _ in range(50000):
            if curr:
                r_checksum += len(curr.val)
                curr = curr.next
                
        res = f"LinkedList node count: {dll.count}, Forward checksum: {f_checksum}, Reversed checksum: {r_checksum}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_21_bitwise_ops.py": '''def xor_crypt(data, key):
    res = []
    key_len = len(key)
    for i in range(len(data)):
        res.append(data[i] ^ ord(key[i % key_len]))
    return res

def bit_shift_left(data, shift_base):
    res = []
    for i, byte in enumerate(data):
        shift = (shift_base + i) % 8
        res.append(((byte << shift) | (byte >> (8 - shift))) & 0xFF)
    return res

def bit_shift_right(data, shift_base):
    res = []
    for i, byte in enumerate(data):
        shift = (shift_base + i) % 8
        res.append(((byte >> shift) | (byte << (8 - shift))) & 0xFF)
    return res

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Rolling XOR encryption and bitwise shifting algorithm.
    Expected duration: 1500-2500ms, Expected memory: <20MB
    """
    try:
        # Generate data
        base_str = "BitwiseOperationSimulationRollingKeyXOREncryptionDecryptionVerification" * 200
        data_bytes = list(base_str.encode('utf-8'))
        key = "GreenLambdaKey"
        
        # Run it 80 times to scale execution time
        final_decrypted = ""
        for iteration in range(80):
            # Encrypt
            encrypted = xor_crypt(data_bytes, key)
            # Shift
            shifted = bit_shift_left(encrypted, 3)
            # Reverse Shift
            unshifted = bit_shift_right(shifted, 3)
            # Decrypt
            decrypted = xor_crypt(unshifted, key)
            final_decrypted = bytes(decrypted).decode('utf-8')
            
        success = final_decrypted == base_str
        res = f"Encryption verified: {success}, TextLen: {len(final_decrypted)}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_22_random_password.py": '''import random
import string

def get_strength_score(pwd):
    score = 0
    if any(c.isupper() for c in pwd):
        score += 25
    if any(c.isdigit() for c in pwd):
        score += 25
    return score

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Simple password verification.
    Expected duration: 100-200ms, Expected memory: <5MB
    """
    try:
        chars = string.ascii_letters + string.digits
        pwd = "".join(random.choices(chars, k=16))
        score = get_strength_score(pwd)
        
        res = f"Password: {pwd[:4]}..., Score: {score}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_23_palindrome_check.py": '''def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Palindrome verification.
    Expected duration: 200-400ms, Expected memory: <5MB
    """
    try:
        words = ["radar", "hello", "level", "world", "noon", "kayak", "stats", "green", "lambda", "cloud"]
        palindromes = [w for w in words if w == w[::-1]]
        res = f"Palindromes found: {palindromes}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_24_counter_collection.py": '''import random

def lambda_handler(event, context):
    """Category 3: Memory Heavy. Large dataset generation, frequency mapping, and manual variance calculation.
    Expected duration: 1000-2000ms, Expected memory: 40-60MB
    """
    try:
        # Generate 1,000,000 numbers in range 0-1000
        nums = [random.randint(0, 1000) for _ in range(1000000)]
        
        # Frequency map
        freq = {}
        for num in nums:
            freq[num] = freq.get(num, 0) + 1
            
        # Top 10
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_freq[:10]
        
        # Mean calculation
        total_sum = sum(nums)
        n = len(nums)
        mean = total_sum / n
        
        # Variance calculation
        sq_diff_sum = sum((x - mean) ** 2 for x in nums)
        variance = sq_diff_sum / n
        
        res = f"Stats calculated on 1M numbers. Mean: {mean:.2f}, Variance: {variance:.2f}, Top1: {top_10[0]}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
''',

    "lambda_25_math_trig.py": '''import math

def factorial(n):
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res

def taylor_sin(x, terms=7):
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi
        
    val = 0.0
    sign = 1
    for i in range(terms):
        power = 2 * i + 1
        val += sign * (x ** power) / factorial(power)
        sign = -sign
    return val

def taylor_cos(x, terms=7):
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi
        
    val = 0.0
    sign = 1
    for i in range(terms):
        power = 2 * i
        val += sign * (x ** power) / factorial(power)
        sign = -sign
    return val

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Taylor series expansions for trigonometry.
    Expected duration: 2500-3500ms, Expected memory: <20MB
    """
    try:
        # Run Taylor series expansions for 14,000 angle values
        total_sin = 0.0
        total_cos = 0.0
        total_tan = 0.0
        
        for i in range(14000):
            angle = (i * 2.0 * math.pi) / 14000
            s = taylor_sin(angle)
            c = taylor_cos(angle)
            total_sin += s
            total_cos += c
            
            if abs(c) > 1e-5:
                total_tan += (s / c)
                
        res = f"Taylor series result: sin_sum={total_sin:.4f}, cos_sum={total_cos:.4f}, tan_sum={total_tan:.4f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
'''
}

for name, content in lambdas.items():
    with open(os.path.join('benchmarks', name), 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Successfully generated {len(lambdas)} high-fidelity benchmark scripts locally.")
