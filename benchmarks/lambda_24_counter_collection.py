from collections import Counter
def lambda_handler(event, context):
    text = 'greenlambda' * 100
    c = Counter(text)
    return {'statusCode': 200, 'body': str(c.most_common(1))}