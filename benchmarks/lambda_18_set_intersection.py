def lambda_handler(event, context):
    s1 = set(range(0, 1000, 2))
    s2 = set(range(0, 1000, 3))
    return {'statusCode': 200, 'body': f'Intersect len: {len(s1.intersection(s2))}'}