import boto3
import json
import sys

def call_lambda_function(client, key):
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

session = boto3.Session(profile_name='schen-gps')
client = session.client('lambda', region_name='us-west-2')

keylist = sys.argv[1]
with open(keylist, 'r') as fh:
    for key in fh:
        key = key.rstrip()
        print('Processing {}'.format(key))
        call_lambda_function(client, key)
