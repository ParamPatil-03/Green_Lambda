import json

def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Deep string serialization and JSON data manipulation.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        records = []
        for i in range(12000):
            # Simulate high depth dictionary record
            rec = {
                "id": i,
                "uuid": f"uuid_record_simulated_{i*13}",
                "active": i % 2 == 0,
                "score": float(i * 1.5),
                "tags": ["cloud", "lambda", "green", f"tag_{i%5}"],
                "metadata": {
                    "env": "production",
                    "region": "ap-south-1",
                    "latency_limit_ms": 150
                }
            }
            records.append(rec)
            
        # Serialize to huge string
        json_data = json.dumps(records)
        
        # Deserialize back
        loaded = json.loads(json_data)
        
        # Validate and edit fields
        valid_count = 0
        for item in loaded:
            if item["id"] >= 0 and "metadata" in item:
                item["score"] += 10.0
                item["metadata"]["env"] = "staging"
                valid_count += 1
                
        # Re-serialize
        final_str = json.dumps(loaded)
        
        res = f"Processed {len(loaded)} records. Valid: {valid_count}, FinalSize: {len(final_str)}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
