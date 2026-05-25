import time

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
