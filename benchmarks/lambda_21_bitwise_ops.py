def lambda_handler(event, context):
    v = 8
    for _ in range(5):
        v = (v << 2) | 1
    return {'statusCode': 200, 'body': str(v)}