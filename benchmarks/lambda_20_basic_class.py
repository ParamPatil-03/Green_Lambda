class Node:
    __slots__ = ['val', 'next', 'prev']
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0
        
    def append(self, val):
        new_node = Node(val)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.count += 1
        
    def reverse(self):
        temp = None
        current = self.head
        self.tail = current
        while current is not None:
            temp = current.prev
            current.prev = current.next
            current.next = temp
            current = current.prev
        if temp is not None:
            self.head = temp.prev

def lambda_handler(event, context):
    """Category 3: Memory Heavy. Double-linked list instantiation, reversal, and searches.
    Expected duration: 1000-2000ms, Expected memory: 50-80MB
    """
    try:
        dll = DoublyLinkedList()
        # Build 100,000 node list with 50-character string payload to inflate memory usage
        payload_base = "GreenLambdaLinkedListPayloadNodeStringData50Chars_"
        for i in range(100000):
            dll.append(f"{payload_base}{i}")
            
        # Forward traversal
        curr = dll.head
        f_checksum = 0
        for _ in range(50000):
            if curr:
                f_checksum += len(curr.val)
                curr = curr.next
                
        # Reverse in place
        dll.reverse()
        
        # Traverse reversed list from head (original tail)
        curr = dll.head
        r_checksum = 0
        for _ in range(50000):
            if curr:
                r_checksum += len(curr.val)
                curr = curr.next
                
        res = f"LinkedList node count: {dll.count}, Forward checksum: {f_checksum}, Reversed checksum: {r_checksum}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
