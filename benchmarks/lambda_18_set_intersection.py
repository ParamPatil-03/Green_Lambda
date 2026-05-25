def lambda_handler(event, context):
    """Category 4: I/O and Data Processing. Multi-set intersections and symmetric differences.
    Expected duration: 1000-2000ms, Expected memory: 20-40MB
    """
    try:
        # Generate 5 large sets with overlapping elements
        set1 = set(x * 2 % 200000 for x in range(100000))
        set2 = set(x * 3 % 200000 for x in range(100000))
        set3 = set(x * 5 % 200000 for x in range(100000))
        set4 = set(x * 7 % 200000 for x in range(100000))
        set5 = set(x * 11 % 200000 for x in range(100000))
        
        sets = [set1, set2, set3, set4, set5]
        
        # All pairwise intersections (10 pairs)
        pairwise_lens = []
        for i in range(5):
            for j in range(i + 1, 5):
                intersect = sets[i].intersection(sets[j])
                pairwise_lens.append(len(intersect))
                
        # Union
        union_set = set1.union(set2).union(set3).union(set4).union(set5)
        
        # Elements in exactly 3 of the 5 sets
        freq = {}
        for s in sets:
            for el in s:
                freq[el] = freq.get(el, 0) + 1
                
        count_exactly_3 = sum(1 for el, f in freq.items() if f == 3)
        
        res = f"Set operations: PairwiseIntersectionsAvg={sum(pairwise_lens)/len(pairwise_lens):.1f}, UnionSize={len(union_set)}, Exactly3SetsCount={count_exactly_3}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
