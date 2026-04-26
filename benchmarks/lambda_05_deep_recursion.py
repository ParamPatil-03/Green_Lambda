def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

def lambda_handler(event, context):
    return {'statusCode': 200, 'body': str(fib(20))}