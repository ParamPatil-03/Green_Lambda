import json
def lambda_handler(event, context):
    d = {'users': [{'i': i} for i in range(1000)]}
    return {'statusCode': 200, 'body': f"Parsed: {len(json.loads(json.dumps(d))['users'])}"}