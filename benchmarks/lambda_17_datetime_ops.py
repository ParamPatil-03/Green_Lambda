import datetime
def lambda_handler(event, context):
    now = datetime.datetime.now()
    return {'statusCode': 200, 'body': now.strftime('%Y-%m-%d %H:%M:%S')}