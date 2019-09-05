import boto3
import json
import sys
import concurrent.futures


def call_lambda_function(client, key):
    key = key.rstrip()
    print(key)
    event = {
            's3_key': key,
            's3_input_bucket': 'scedc-pds',
            's3_output_bucket': 'lambda-decimated',
            'decimation_factor': 4
           }
     
    response = client.invoke(
                               FunctionName='SCEDCFunction',
                               InvocationType='Event',
                               LogType='Tail',
                               Payload=json.dumps(event)
                              )

if len(sys.argv) < 2:
    print('usage: {} filename'.format(sys.argv[0]))
    sys.exit(2)
keylist = sys.argv[1]

session = boto3.Session(profile_name='schen-gps')
client = session.client('lambda', region_name='us-west-2')

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    with open(keylist, 'r') as fh:
        futures = [executor.submit(call_lambda_function, client, key) for key in fh.readlines()]
        print('Executing total', len(futures), 'jobs')
        for idx, future in enumerate(concurrent.futures.as_completed(futures, timeout=100.0)):
            res = future.result()
            print('Processed job', idx, 'result', res)
