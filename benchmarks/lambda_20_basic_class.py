class Worker:
    def __init__(self, val):
        self.val = val
    def get(self):
        return self.val * 2
def lambda_handler(event, context):
    w = Worker(15)
    return {'statusCode': 200, 'body': str(w.get())}