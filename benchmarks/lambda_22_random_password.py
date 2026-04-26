import random, string
def lambda_handler(event, context):
    pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return {'statusCode': 200, 'body': pwd}