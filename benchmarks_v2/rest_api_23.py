import json
import hashlib
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        iterations = 2300
        headers = event.get('headers', {}) or {}
        query_params = event.get('queryStringParameters', {}) or {}
        
        token = headers.get('Authorization', 'Bearer dummy-token-23')
        h = hashlib.sha256()
        
        # Heavy computation
        for j in range(iterations):
            h.update(f"{token}-{j}".encode('utf-8'))
        token_hash = h.hexdigest()
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < 0.0:
            h.update(b"additional-busy-wait-cycles")
            token_hash = h.hexdigest()
            
        route = query_params.get('route', 'default')
        if route == 'users':
            data = {"status": "ok", "users": [f"user_{x}" for x in range(230)]}
        elif route == 'posts' and 23 % 2 == 0:
            data = {"status": "ok", "posts": [f"post_{x}" for x in range(115)]}
        elif route == 'comments' and 23 % 3 == 0:
            data = {"status": "ok", "comments": [f"comment_{x}" for x in range(184)]}
        else:
            data = {"status": "ok", "message": "Welcome to REST API 23!"}
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'api': 'rest_api_23',
                'hash': token_hash,
                'data': data
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
