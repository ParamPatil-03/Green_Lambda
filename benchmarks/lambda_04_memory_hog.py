def lambda_handler(event, context):
    # Highly safe size to prevent OOM
    big_list = ['A'] * 500000
    return {'statusCode': 200, 'body': f'Len: {len(big_list)}'}