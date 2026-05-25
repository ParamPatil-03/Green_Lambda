def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Heavy tuple unpacking, grouping, and sorting.
    Expected duration: 1500-2500ms, Expected memory: 20-40MB
    """
    try:
        # Generate 400,000 tuples of (id, value, category, score)
        data = []
        for i in range(400000):
            cat = f"cat_{i % 10}"
            score = float((i * 19 % 1000) / 10.0)
            data.append((i, f"data_val_{i}", cat, score))
            
        # Unpack and group by category
        groups = {}
        for item in data:
            idx, val, cat, score = item
            if cat not in groups:
                groups[cat] = []
            groups[cat].append((idx, score))
            
        # Sort each group by score and keep top 100
        top_scores = {}
        for cat, items in groups.items():
            items.sort(key=lambda x: x[1], reverse=True)
            top_scores[cat] = items[:100]
            
        # Compute average of top scores
        avg_top_scores = {}
        for cat, items in top_scores.items():
            avg_top_scores[cat] = sum(x[1] for x in items) / len(items)
            
        res = f"Processed {len(data)} tuples. Groups count: {len(groups)}, AvgTopScores: {list(avg_top_scores.items())[:3]}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
