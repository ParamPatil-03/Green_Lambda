import json
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        inside = 0
        total = 46000
        
        state = 42
        for step in range(total):
            state = (state * 1103515245 + 12345) & 0x7fffffff
            x = state / 2147483647.0
            state = (state * 1103515245 + 12345) & 0x7fffffff
            y = state / 2147483647.0
            
            if x*x + y*y <= 1.0:
                inside += 1
                
        pi_estimate = 4.0 * inside / total
        
        n_intervals = 2300
        dx = 10.0 / n_intervals
        integral_sum = 0.5 * (0.0 + 100.0)
        for step in range(1, n_intervals):
            x_val = step * dx
            integral_sum += x_val * x_val
        integral_sum *= dx
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < 0.0:
            # Simulating busy loops
            state = (state * 1103515245 + 12345) & 0x7fffffff
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'scientific': 'scientific_calc_23',
                'pi_estimate': pi_estimate,
                'integral': integral_sum,
                'iterations': total
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
