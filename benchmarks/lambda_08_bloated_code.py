def lambda_handler(event, context):
    a=1;b=2;c=3;d=4;e=5;f=6
    v1='t1';v2='t2';v3='t3';v4='t4'
    return {'statusCode': 200, 'body': str(a+b+c+d+e+f)}