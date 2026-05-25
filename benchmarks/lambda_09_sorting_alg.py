import random
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
