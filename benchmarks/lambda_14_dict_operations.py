def lambda_handler(event, context):
    d = {str(i): i*2 for i in range(1000)}
    summ = sum(d.values())
    return {'statusCode': 200, 'body': str(summ)}