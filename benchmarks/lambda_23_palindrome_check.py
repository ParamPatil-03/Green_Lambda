def is_pal(w):
    return w == w[::-1]
def lambda_handler(event, context):
    words = ['radar', 'stats', 'hello', 'world', 'level', 'kayak'] * 100
    pals = [w for w in words if is_pal(w)]
    return {'statusCode': 200, 'body': f'Palindromes: {len(pals)}'}