def lambda_handler(event, context):
    long_str = 'GreenLambdaOptimization' * 500
    return {'statusCode': 200, 'body': long_str[::-1][:50]}