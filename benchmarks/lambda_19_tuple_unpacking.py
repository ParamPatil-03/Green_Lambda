def lambda_handler(event, context):
    coords = [(i, i+1) for i in range(500)]
    res = sum((x * y) for x, y in coords)
    return {'statusCode': 200, 'body': str(res)}