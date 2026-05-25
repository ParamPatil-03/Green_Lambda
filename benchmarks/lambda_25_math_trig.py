import math

def factorial(n):
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res

def taylor_sin(x, terms=7):
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi
        
    val = 0.0
    sign = 1
    for i in range(terms):
        power = 2 * i + 1
        val += sign * (x ** power) / factorial(power)
        sign = -sign
    return val

def taylor_cos(x, terms=7):
    x = x % (2 * math.pi)
    if x > math.pi:
        x -= 2 * math.pi
    elif x < -math.pi:
        x += 2 * math.pi
        
    val = 0.0
    sign = 1
    for i in range(terms):
        power = 2 * i
        val += sign * (x ** power) / factorial(power)
        sign = -sign
    return val

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Taylor series expansions for trigonometry.
    Expected duration: 2500-3500ms, Expected memory: <20MB
    """
    try:
        # Run Taylor series expansions for 14,000 angle values
        total_sin = 0.0
        total_cos = 0.0
        total_tan = 0.0
        
        for i in range(14000):
            angle = (i * 2.0 * math.pi) / 14000
            s = taylor_sin(angle)
            c = taylor_cos(angle)
            total_sin += s
            total_cos += c
            
            if abs(c) > 1e-5:
                total_tan += (s / c)
                
        res = f"Taylor series result: sin_sum={total_sin:.4f}, cos_sum={total_cos:.4f}, tan_sum={total_tan:.4f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
