import datetime

def lambda_handler(event, context):
    """Category 5: Lightweight/Baseline. Basic date computations.
    Expected duration: 200-400ms, Expected memory: <5MB
    """
    try:
        base_date = datetime.datetime(2023, 1, 1)
        dates = [base_date + datetime.timedelta(days=i*5) for i in range(10)]
        
        deltas = []
        for i in range(len(dates) - 1):
            delta = dates[i+1] - dates[i]
            deltas.append(delta.days)
            
        formatted = [d.strftime('%Y-%m-%d') for d in dates]
        
        res = f"First: {formatted[0]}, Last: {formatted[-1]}, Deltas: {deltas}"
        return {'statusCode': 200, 'body': res}
    except Exception as e:
        return {'statusCode': 500, 'body': f"Error: {str(e)}"}
