def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Large dictionary manipulations and set operations.
    Expected duration: 1000-2000ms, Expected memory: 20-40MB
    """
    try:
        # Create dicts
        dict1 = {f"key_{i}": f"val_{i % 100}" for i in range(50000)}
        dict2 = {f"key_{i}": f"val_{(i + 10) % 100}" for i in range(25000, 75000)}
        dict3 = {f"key_{i}": f"val_{i % 50}" for i in range(10000, 60000)}
        
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        keys3 = set(dict3.keys())
        
        # Intersections/Unions
        common_keys = keys1.intersection(keys2).intersection(keys3)
        all_keys = keys1.union(keys2).union(keys3)
        diff_keys = keys1.difference(keys2)
        
        # Build inverted index
        inverted = {}
        for k in common_keys:
            val = dict1[k]
            if val not in inverted:
                inverted[val] = []
            inverted[val].append(k)
            
        # Value frequency count
        val_counts = {v: len(keys) for v, keys in inverted.items()}
        sorted_counts = sorted(val_counts.items(), key=lambda x: x[1], reverse=True)
        
        res = f"Dict operations. CommonKeys: {len(common_keys)}, UnionKeys: {len(all_keys)}, DiffKeys: {len(diff_keys)}, TopFreq: {sorted_counts[:3]}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
