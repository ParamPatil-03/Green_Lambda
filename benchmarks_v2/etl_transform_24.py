import json
import time

def lambda_handler(event, context):
    try:
        start_time = time.time()
        rows = []
        for r in range(6000):
            rows.append({
                'id': r,
                'category': f"cat_{r % 12}",
                'value': float(r * 1.5),
                'active': (r % 2 == 0)
            })
            
        transformed = []
        aggregates = {}
        for row in rows:
            if row['active']:
                new_val = (row['value'] * 1.12) / 0.95
                transformed.append({
                    'id': row['id'],
                    'cat': row['category'].upper(),
                    'val': new_val
                })
                cat = row['category']
                aggregates[cat] = aggregates.get(cat, 0.0) + new_val
                
        # Calibrated duration loop for high-duration training coverage
        while time.time() - start_time < 0.0:
            # Simulating additional ETL transformations
            for row in rows[:1000]:
                dummy = (row['value'] * 1.05) / 0.99
                
        return {
            'statusCode': 200,
            'body': json.dumps({
                'etl': 'etl_transform_24',
                'processed_rows': len(rows),
                'transformed_rows': len(transformed),
                'category_totals': aggregates
            })
        }
    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}
