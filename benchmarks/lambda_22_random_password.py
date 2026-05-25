import random
import string

def get_strength_score(pwd):
    score = 0
    if any(c.isupper() for c in pwd):
        score += 25
    if any(c.isdigit() for c in pwd):
        score += 25
    return score

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Simple password verification.
    Expected duration: 100-200ms, Expected memory: <5MB
    """
    try:
        chars = string.ascii_letters + string.digits
        pwd = "".join(random.choices(chars, k=16))
        score = get_strength_score(pwd)
        
        res = f"Password: {pwd[:4]}..., Score: {score}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
