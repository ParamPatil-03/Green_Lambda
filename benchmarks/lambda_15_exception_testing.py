def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Basic exception handling check.
    Expected duration: 50-200ms, Expected memory: <5MB
    """
    successes = 0
    failures = 0
    
    try:
        _ = 1 / 0
        successes += 1
    except ZeroDivisionError:
        failures += 1
        
    try:
        d = {}
        _ = d["missing"]
        successes += 1
    except KeyError:
        failures += 1
        
    try:
        _ = int("not_a_number")
        successes += 1
    except ValueError:
        failures += 1
        
    res = f"Exception tests. Success: {successes}, Failures: {failures}"
    return {'statusCode': 200, 'body': res}
