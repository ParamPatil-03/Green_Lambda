def lambda_handler(event, context):
    text = 'test_' * 1000
    return {'statusCode': 200, 'body': str(len(text.replace('_', '-').upper()))}