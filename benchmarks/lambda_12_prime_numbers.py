def sieve_of_eratosthenes(limit):
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
