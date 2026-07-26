import json
import math
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        x_vec = [float((idx * 1.7) % 5.0) for idx in range(50)]
        
        classes = ['Green', 'Amber', 'Red']
        scores = {c: 0.0 for c in classes}
        
        for c in classes:
            prior = 0.33
            score = math.log(prior)
            for f_idx, val in enumerate(x_vec):
                mean = float((f_idx * 1.1) % 4.0)
                var = 1.0 + float((f_idx * 0.2) % 2.0)
                likelihood = (1.0 / math.sqrt(2.0 * math.pi * var)) * math.exp(-((val - mean) ** 2) / (2.0 * var))
                score += math.log(max(1e-9, likelihood))
            scores[c] = score
            
        predicted_class = max(scores, key=scores.get)
        
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < 0.0:
            # Simulating additional classifier steps
            dummy_calc = math.sin(x_vec[0]) * math.cos(x_vec[-1])
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'ml': 'ml_inference_10',
                'features_count': len(x_vec),
                'prediction': predicted_class,
                'scores': scores
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
