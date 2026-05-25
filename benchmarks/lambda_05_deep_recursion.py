import sys
sys.setrecursionlimit(10000)

class BSTNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def insert_bst(root, val):
    if root is None:
        return BSTNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root

def inorder_traverse(root, result):
    if root:
        inorder_traverse(root.left, result)
        result.append(root.val)
        inorder_traverse(root.right, result)

def merge_sort_rec(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort_rec(arr[:mid])
    right = merge_sort_rec(arr[mid:])
    
    # Merge step
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

def binary_search_rec(arr, low, high, x):
    if high >= low:
        mid = (high + low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search_rec(arr, low, mid - 1, x)
        else:
            return binary_search_rec(arr, mid + 1, high, x)
    return -1

def lambda_handler(event, context):
    """Category 2: High Complexity/Recursive. Recursive sorting, binary search, and BST traversal.
    Expected duration: 1500-2500ms, Expected memory: 15-35MB
    """
    try:
        total_sorted_len = 0
        search_hits = 0
        bst_traversed_len = 0
        
        for iteration in range(25):
            arr = [(x * 123 % 5000) for x in range(2000)]
            sorted_arr = merge_sort_rec(arr)
            total_sorted_len += len(sorted_arr)
            
            for target in [100, 200, 300, 400, 500]:
                idx = binary_search_rec(sorted_arr, 0, len(sorted_arr) - 1, target)
                if idx != -1:
                    search_hits += 1
                    if target % 200 == 0:
                        search_hits += 10
                    elif target % 300 == 0:
                        search_hits += 5
                    else:
                        search_hits += 1
                else:
                    if target > 300:
                        search_hits -= 1
                        
            if iteration < 3:
                root = None
                for val in sorted_arr[:300]:
                    if val % 2 == 0:
                        root = insert_bst(root, val)
                    else:
                        root = insert_bst(root, val + 1)
                bst_res = []
                inorder_traverse(root, bst_res)
                bst_traversed_len += len(bst_res)
                
        res = f"Sorted len: {total_sorted_len}, Search hits: {search_hits}, BST inorder: {bst_traversed_len}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
