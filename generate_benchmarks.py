import os

os.makedirs('benchmarks', exist_ok=True)

lambdas = {
    # Original 10, enhanced for absolute crash-proof safety
    "lambda_01_hello.py": "def lambda_handler(event, context):\n    return {'statusCode': 200, 'body': 'Hello World. Baseline'}",
    "lambda_02_math_heavy.py": "def lambda_handler(event, context):\n    res = sum(i * 0.5 for i in range(100000))\n    return {'statusCode': 200, 'body': str(res)}",
    "lambda_03_high_complexity.py": "def lambda_handler(event, context):\n    v = event.get('v', 0)\n    return {'statusCode': 200, 'body': 'Even' if v % 2 == 0 else 'Odd'}",
    "lambda_04_memory_hog.py": "def lambda_handler(event, context):\n    # Highly safe size to prevent OOM\n    big_list = ['A'] * 500000\n    return {'statusCode': 200, 'body': f'Len: {len(big_list)}'}",
    "lambda_05_deep_recursion.py": "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)\n\ndef lambda_handler(event, context):\n    return {'statusCode': 200, 'body': str(fib(20))}",
    "lambda_06_string_ops.py": "def lambda_handler(event, context):\n    text = 'test_' * 1000\n    return {'statusCode': 200, 'body': str(len(text.replace('_', '-').upper()))}",
    "lambda_07_io_simulated.py": "import time\ndef lambda_handler(event, context):\n    time.sleep(1)\n    return {'statusCode': 200, 'body': 'IO simulated.'}",
    "lambda_08_bloated_code.py": "def lambda_handler(event, context):\n    a=1;b=2;c=3;d=4;e=5;f=6\n    v1='t1';v2='t2';v3='t3';v4='t4'\n    return {'statusCode': 200, 'body': str(a+b+c+d+e+f)}",
    "lambda_09_sorting_alg.py": "import random\ndef lambda_handler(event, context):\n    arr = [random.randint(1, 1000) for _ in range(2000)]\n    arr.sort()\n    return {'statusCode': 200, 'body': f'Min: {arr[0]}'}",
    "lambda_10_json_parsing.py": "import json\ndef lambda_handler(event, context):\n    d = {'users': [{'i': i} for i in range(1000)]}\n    return {'statusCode': 200, 'body': f\"Parsed: {len(json.loads(json.dumps(d))['users'])}\"}",
    
    # 15 NEW Completely Crash-Proof Codes (Zero external dependencies)
    "lambda_11_list_comprehension.py": "def lambda_handler(event, context):\n    # Filter evens\n    evens = [x for x in range(5000) if x % 2 == 0]\n    return {'statusCode': 200, 'body': f'Count: {len(evens)}'}",
    
    "lambda_12_prime_numbers.py": "def lambda_handler(event, context):\n    primes = []\n    for num in range(2, 500):\n        for i in range(2, num):\n            if (num % i) == 0:\n                break\n        else:\n            primes.append(num)\n    return {'statusCode': 200, 'body': f'Primes found: {len(primes)}'}",
    
    "lambda_13_string_reversal.py": "def lambda_handler(event, context):\n    long_str = 'GreenLambdaOptimization' * 500\n    return {'statusCode': 200, 'body': long_str[::-1][:50]}",
    
    "lambda_14_dict_operations.py": "def lambda_handler(event, context):\n    d = {str(i): i*2 for i in range(1000)}\n    summ = sum(d.values())\n    return {'statusCode': 200, 'body': str(summ)}",
    
    "lambda_15_exception_testing.py": "def lambda_handler(event, context):\n    try:\n        raise ValueError('Simulated Error')\n    except ValueError as e:\n        return {'statusCode': 200, 'body': f'Caught: {str(e)}'}",
    
    "lambda_16_nested_loops.py": "def lambda_handler(event, context):\n    count = 0\n    for i in range(100):\n        for j in range(100):\n            count += i + j\n    return {'statusCode': 200, 'body': str(count)}",
    
    "lambda_17_datetime_ops.py": "import datetime\ndef lambda_handler(event, context):\n    now = datetime.datetime.now()\n    return {'statusCode': 200, 'body': now.strftime('%Y-%m-%d %H:%M:%S')}",
    
    "lambda_18_set_intersection.py": "def lambda_handler(event, context):\n    s1 = set(range(0, 1000, 2))\n    s2 = set(range(0, 1000, 3))\n    return {'statusCode': 200, 'body': f'Intersect len: {len(s1.intersection(s2))}'}",
    
    "lambda_19_tuple_unpacking.py": "def lambda_handler(event, context):\n    coords = [(i, i+1) for i in range(500)]\n    res = sum((x * y) for x, y in coords)\n    return {'statusCode': 200, 'body': str(res)}",
    
    "lambda_20_basic_class.py": "class Worker:\n    def __init__(self, val):\n        self.val = val\n    def get(self):\n        return self.val * 2\ndef lambda_handler(event, context):\n    w = Worker(15)\n    return {'statusCode': 200, 'body': str(w.get())}",
    
    "lambda_21_bitwise_ops.py": "def lambda_handler(event, context):\n    v = 8\n    for _ in range(5):\n        v = (v << 2) | 1\n    return {'statusCode': 200, 'body': str(v)}",
    
    "lambda_22_random_password.py": "import random, string\ndef lambda_handler(event, context):\n    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=32))\n    return {'statusCode': 200, 'body': pwd}",
    
    "lambda_23_palindrome_check.py": "def is_pal(w):\n    return w == w[::-1]\ndef lambda_handler(event, context):\n    words = ['radar', 'stats', 'hello', 'world', 'level', 'kayak'] * 100\n    pals = [w for w in words if is_pal(w)]\n    return {'statusCode': 200, 'body': f'Palindromes: {len(pals)}'}",
    
    "lambda_24_counter_collection.py": "from collections import Counter\ndef lambda_handler(event, context):\n    text = 'greenlambda' * 100\n    c = Counter(text)\n    return {'statusCode': 200, 'body': str(c.most_common(1))}",
    
    "lambda_25_math_trig.py": "import math\ndef lambda_handler(event, context):\n    sines = [math.sin(i) for i in range(1000)]\n    return {'statusCode': 200, 'body': str(sum(sines))}"
}

for name, content in lambdas.items():
    with open(os.path.join('benchmarks', name), 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Successfully generated {len(lambdas)} ultra-safe benchmark scripts locally.")
