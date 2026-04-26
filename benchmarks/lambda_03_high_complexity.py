def lambda_handler(event, context):
    v = event.get('v', 0)
    return {'statusCode': 200, 'body': 'Even' if v % 2 == 0 else 'Odd'}