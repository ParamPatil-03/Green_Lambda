def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Simple string operations.
    Expected duration: 100-300ms, Expected memory: <5MB
    """
    try:
        base = "GreenLambdaOptimizationBaseline" * 40
        upper_str = base.upper()
        lower_str = base.lower()
        replaced = base.replace("e", "3").replace("a", "4")
        substring = base[10:100]
        words_len = len(base.split("a"))
        
        res = f"Upper: {upper_str[:10]}, Lower: {lower_str[:10]}, Replaced: {replaced[:10]}, Sub: {substring}, SplitLen: {words_len}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
