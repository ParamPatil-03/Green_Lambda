def lambda_handler(event, context):
    res = sum(i * 0.5 for i in range(100000))
    return {'statusCode': 200, 'body': str(res)}