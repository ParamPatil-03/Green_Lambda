import math

def get_cofactor(matrix, i, j):
    res = []
    for r in range(len(matrix)):
        if r != i:
            row = []
            for c in range(len(matrix[r])):
                if c != j:
                    row.append(matrix[r][c])
            res.append(row)
    return res

def get_determinant(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0
    sign = 1
    for j in range(n):
        cof = get_cofactor(matrix, 0, j)
        det += sign * matrix[0][j] * get_determinant(cof)
        sign = -sign
    return det

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Computes cofactor expansion determinant and factorial series.
    Expected duration: 3000-4000ms, Expected memory: <20MB
    """
    try:
        # Run cofactor expansion determinant on multiple 5x5 matrices to burn CPU
        total = 0.0
        matrix = [
            [3.1, 2.4, 5.6, 0.8, 1.2],
            [0.5, 4.2, 1.7, 9.3, 2.1],
            [1.2, 0.9, 8.5, 4.4, 3.3],
            [5.5, 1.1, 0.2, 7.8, 6.9],
            [2.2, 3.3, 4.4, 5.5, 0.1]
        ]
        # Run it 600 times to scale execution time
        for i in range(600):
            det = get_determinant(matrix)
            # Slightly perturb matrix to avoid CPU caching optimizations
            matrix[0][0] = (matrix[0][0] + 0.0001) % 10.0
            total += det
        
        # Burn a bit more CPU with floating-point expansions
        val = 0.0
        for x in range(1, 20000):
            val += math.sqrt(x) * math.log(x)
            
        return {'statusCode': 200, 'body': f"Determinant sum: {total:.4f}, Val: {val:.4f}"}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
