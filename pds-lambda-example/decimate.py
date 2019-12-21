import boto3
import json
import sys
import concurrent.futures
from settings import *

def call_lambda_function(client, key):
    key = key.rstrip()
    print(key)
    event = {
            's3_key': key,
            's3_input_bucket': INPUT_BUCKET,
            's3_output_bucket': OUTPUT_BUCKET,
            'decimation_factor': 4
           }
     
    response = client.invoke(
                               FunctionName=LAMBDA_FUNCTION,
                               InvocationType='Event',
                               LogType='Tail',
                               Payload=json.dumps(event)
                              )

if len(sys.argv) < 2:
    print('usage: {} filename'.format(sys.argv[0]))
    sys.exit(2)
keylist = sys.argv[1]

session = boto3.Session(profile_name=AWS_PROFILE)
client = session.client('lambda', region_name=AWS_REGION)

with concurrent.futures.ThreadPoolExecutor(max_workers=NCORES) as executor:
    with open(keylist, 'r') as fh:
        futures = [executor.submit(call_lambda_function, client, key) for key in fh.readlines()]
        print('Executing total', len(futures), 'jobs')
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            print('Processed job', idx, 'result', res)
