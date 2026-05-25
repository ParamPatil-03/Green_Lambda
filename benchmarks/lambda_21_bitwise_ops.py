def xor_crypt(data, key):
    res = []
    key_len = len(key)
    for i in range(len(data)):
        res.append(data[i] ^ ord(key[i % key_len]))
    return res

def bit_shift_left(data, shift_base):
    res = []
    for i, byte in enumerate(data):
        shift = (shift_base + i) % 8
        res.append(((byte << shift) | (byte >> (8 - shift))) & 0xFF)
    return res

def bit_shift_right(data, shift_base):
    res = []
    for i, byte in enumerate(data):
        shift = (shift_base + i) % 8
        res.append(((byte >> shift) | (byte << (8 - shift))) & 0xFF)
    return res

def lambda_handler(event, context):
    """Category 1: CPU Heavy. Rolling XOR encryption and bitwise shifting algorithm.
    Expected duration: 1500-2500ms, Expected memory: <20MB
    """
    try:
        # Generate data
        base_str = "BitwiseOperationSimulationRollingKeyXOREncryptionDecryptionVerification" * 200
        data_bytes = list(base_str.encode('utf-8'))
        key = "GreenLambdaKey"
        
        # Run it 80 times to scale execution time
        final_decrypted = ""
        for iteration in range(80):
            # Encrypt
            encrypted = xor_crypt(data_bytes, key)
            # Shift
            shifted = bit_shift_left(encrypted, 3)
            # Reverse Shift
            unshifted = bit_shift_right(shifted, 3)
            # Decrypt
            decrypted = xor_crypt(unshifted, key)
            final_decrypted = bytes(decrypted).decode('utf-8')
            
        success = final_decrypted == base_str
        res = f"Encryption verified: {success}, TextLen: {len(final_decrypted)}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
