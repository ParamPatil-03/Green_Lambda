def lambda_handler(event, context):
    count = 0
    for i in range(100):
        for j in range(100):
            count += i + j
    return {'statusCode': 200, 'body': str(count)}