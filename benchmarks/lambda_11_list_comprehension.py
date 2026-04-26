def lambda_handler(event, context):
    # Filter evens
    evens = [x for x in range(5000) if x % 2 == 0]
    return {'statusCode': 200, 'body': f'Count: {len(evens)}'}