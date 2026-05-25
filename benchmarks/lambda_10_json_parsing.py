import json

def build_nested_structure(depth, width):
    if depth == 0:
        return {"value": 1.5, "flag": True, "label": "leaf"}
    res = {}
    for i in range(width):
        res[f"key_{i}"] = build_nested_structure(depth - 1, width)
    return res

def collect_values(obj, results):
    if isinstance(obj, dict):
        if "value" in obj:
            results.append(obj["value"])
        for k, v in obj.items():
            if k != "value":
                collect_values(v, results)
    elif isinstance(obj, list):
        for item in obj:
            collect_values(item, results)

def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Nested JSON generation, parsing, and traversal.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        # Build nested data tree (depth=4, width=8 gives 8^4 = 4096 leaves)
        tree = build_nested_structure(4, 8)
        
        # Serialize
        serialized = json.dumps(tree)
        
        # Deserialize
        deserialized = json.loads(serialized)
        
        # Collect values recursively
        values = []
        collect_values(deserialized, values)
        
        # Compute stats
        v_sum = sum(values)
        v_avg = v_sum / len(values) if values else 0.0
        
        res = f"Traversed nested JSON. Leaves count: {len(values)}, Sum: {v_sum:.2f}, Avg: {v_avg:.2f}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
