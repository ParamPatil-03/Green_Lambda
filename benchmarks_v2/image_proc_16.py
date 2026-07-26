import json
import math
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        pixels = [[float((r * c) % 256) for c in range(192)] for r in range(192)]
        
        filtered = [[0.0 for _ in range(192)] for _ in range(192)]
        kernel_sum = 0.0
        
        for loop in range(1):
            for r in range(1, 192 - 1):
                for c in range(1, 192 - 1):
                    val = (
                        pixels[r-1][c-1] + pixels[r-1][c] + pixels[r-1][c+1] +
                        pixels[r][c-1]   + pixels[r][c]   + pixels[r][c+1] +
                        pixels[r+1][c-1] + pixels[r+1][c] + pixels[r+1][c+1]
                    ) / 9.0
                    filtered[r][c] = val
                    if loop == 0:
                        kernel_sum += val
                        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < 0.0:
            # Simulating additional pixel manipulation runs
            dummy_sum = sum(filtered[0])
            
        resized = []
        for r in range(0, 192, 2):
            row = []
            for c in range(0, 192, 2):
                row.append(filtered[r][c])
            resized.append(row)
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'image': 'image_proc_16',
                'original_dim': '192x192',
                'resized_dim': f"{len(resized)}x{len(resized[0]) if resized else 0}",
                'pixel_sum': kernel_sum
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
