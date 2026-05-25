def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Palindrome verification.
    Expected duration: 200-400ms, Expected memory: <5MB
    """
    try:
        words = ["radar", "hello", "level", "world", "noon", "kayak", "stats", "green", "lambda", "cloud"]
        palindromes = [w for w in words if w == w[::-1]]
        res = f"Palindromes found: {palindromes}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
