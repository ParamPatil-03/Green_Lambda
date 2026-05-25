def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Deeply nested loops and multi-level calculations.
    Expected duration: 2000-3000ms, Expected memory: 15-35MB
    """
    try:
        dim_x = 50
        dim_y = 50
        dim_z = 10
        
        accumulator = 0.0
        for iteration in range(5):
            for x in range(dim_x):
                for y in range(dim_y):
                    for z in range(dim_z):
                        if (x + y + z) % 2 == 0:
                            for step in range(5):
                                val = (x * 0.1) + (y * 0.2) + (z * 0.3) + (step * 0.01)
                                if val > 15.0:
                                    if val < 20.0:
                                        accumulator += val * 1.5
                                    else:
                                        accumulator += val
                                else:
                                    if val > 5.0:
                                        accumulator -= val * 0.5
                                    else:
                                        accumulator -= val
                        else:
                            if x % 3 == 0:
                                accumulator += (x * y * z * 0.001)
                            else:
                                accumulator -= (x * y * z * 0.0005)
                                
        res = f"Deeply nested matrix calculation. Accumulator: {accumulator:.4f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
