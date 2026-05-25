import os
import datetime

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Returns basic system and region metadata.
    Expected duration: <100ms, Expected memory: <5MB
    """
    try:
        region = os.environ.get('AWS_REGION', 'us-east-1')
        timestamp = datetime.datetime.now().isoformat()
        res = f"Hello from Green Lambda! Region: {region}, Timestamp: {timestamp}, Status: ACTIVE"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
