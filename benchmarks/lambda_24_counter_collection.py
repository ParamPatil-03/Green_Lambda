import random

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
