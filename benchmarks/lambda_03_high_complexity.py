def classify_point(x, y, z, w, v):
    # Deep nesting with if/elif/else to generate high cyclomatic complexity
    if x > 0.5:
        if y < 0.3:
            if z > 0.7:
                if w == 'A':
                    if v % 2 == 0:
                        return 1
                    else:
                        return 2
                else:
                    return 3
            else:
                if w == 'B':
                    return 4
                else:
                    return 5
        else:
            if z < 0.4:
                if w == 'A':
                    return 6
                else:
                    return 7
            else:
                return 8
    else:
        if y > 0.6:
            if z < 0.2:
                if w == 'C':
                    return 9
                else:
                    return 10
            else:
                if w == 'A':
                    return 11
                else:
                    return 12
        else:
            if z > 0.5:
                if v % 3 == 0:
                    return 13
                else:
                    return 14
            else:
                return 15

def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Pure Python Decision Tree Classifier.
    Expected duration: 1500-2500ms, Expected memory: 15-35MB
    """
    try:
        # Classify 12,000 synthetic data points to consume CPU time
        counts = [0] * 16
        for i in range(12000):
            x = (i * 17 % 100) / 100.0
            y = (i * 23 % 100) / 100.0
            z = (i * 31 % 100) / 100.0
            w = ['A', 'B', 'C', 'D'][i % 4]
            v = i
            cls = classify_point(x, y, z, w, v)
            counts[cls] += 1
            
        res = f"Class counts: {counts}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
