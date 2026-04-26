def lambda_handler(event, context):
    try:
        raise ValueError('Simulated Error')
    except ValueError as e:
        return {'statusCode': 200, 'body': f'Caught: {str(e)}'}