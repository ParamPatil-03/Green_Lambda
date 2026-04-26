import math
def lambda_handler(event, context):
    sines = [math.sin(i) for i in range(1000)]
    return {'statusCode': 200, 'body': str(sum(sines))}