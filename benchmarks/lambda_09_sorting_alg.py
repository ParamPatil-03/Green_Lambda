import random
def lambda_handler(event, context):
    arr = [random.randint(1, 1000) for _ in range(2000)]
    arr.sort()
    return {'statusCode': 200, 'body': f'Min: {arr[0]}'}