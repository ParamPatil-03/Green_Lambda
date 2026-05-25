def lambda_handler(event, context):
    """Category 3: Memory Heavy. Matrix operations on a large 2D list of float values.
    Expected duration: 1000-2000ms, Expected memory: 50-70MB
    """
    try:
        rows = 1000
        cols = 500
        # Build large 2D grid
        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                row.append(float(r * c * 0.001))
            grid.append(row)
            
        # Row sums
        row_sums = [sum(row) for row in grid]
        
        # Column sums (intensive loop)
        col_sums = [0.0] * cols
        for c in range(cols):
            c_sum = 0.0
            for r in range(rows):
                c_sum += grid[r][c]
            col_sums[c] = c_sum
            
        # Find min and max
        min_val = grid[0][0]
        max_val = grid[0][0]
        for row in grid:
            for val in row:
                if val < min_val:
                    min_val = val
                elif val > max_val:
                    max_val = val
                    
        res = f"Grid processed: min={min_val:.3f}, max={max_val:.3f}, sum_row0={row_sums[0]:.3f}, sum_col0={col_sums[0]:.3f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
