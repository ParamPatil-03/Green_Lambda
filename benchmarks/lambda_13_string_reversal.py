def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Reversing strings and simple palindrome checks.
    Expected duration: 100-300ms, Expected memory: <5MB
    """
    try:
        s1 = "abcdefghijklmnopqrstuvwxyz" * 20
        s2 = "ReverseMeGreenLambda" * 20
        
        rev1 = s1[::-1]
        rev2 = s2[::-1]
        
        is_pal1 = s1 == rev1
        is_pal2 = s2 == rev2
        
        res = f"Rev1Prefix: {rev1[:10]}, Rev2Prefix: {rev2[:10]}, IsPal1: {is_pal1}, IsPal2: {is_pal2}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
