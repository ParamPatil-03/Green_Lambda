def lambda_handler(event, context):
    """Category 3: Memory Heavy. Allocates large lists and dictionaries to stress memory.
    Expected duration: 800-1500ms, Expected memory: 60-80MB
    """
    try:
        # 1. Allocate large lists
        str_list = [f"MemoryHogDataElement_{i}" for i in range(400000)]
        
        # 2. Dictionary with 80,000 key-value pairs
        data_dict = {f"key_{i}": f"value_{i*2}" for i in range(80000)}
        
        # 3. Tuple structures
        tuples_list = [(i, i+1, i+2, i+3, i+4, i+5, i+6, i+7, i+8, i+9) for i in range(10000)]
        
        # Access elements to verify allocation and prevent optimization garbage collection
        str_checksum = sum(1 for s in str_list if len(s) > 20)
        dict_checksum = sum(1 for k in data_dict if k.startswith("key_5"))
        tuple_sum = sum(t[5] for t in tuples_list)
        
        res = f"Allocated structures. Checksums: str_list={str_checksum}, dict={dict_checksum}, tuple_sum={tuple_sum}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
