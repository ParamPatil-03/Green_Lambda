def lambda_handler(event, context):
    primes = []
    for num in range(2, 500):
        for i in range(2, num):
            if (num % i) == 0:
                break
        else:
            primes.append(num)
    return {'statusCode': 200, 'body': f'Primes found: {len(primes)}'}