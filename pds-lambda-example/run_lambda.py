"""
run_lambda.py runs the lambda function on one seismogram.
"""

import boto3
import json
from settings import *

session = boto3.Session(profile_name=AWS_PROFILE)
client = session.client('lambda', region_name=AWS_REGION)

event = {
  's3_input_bucket': INPUT_BUCKET,
  's3_output_bucket': OUTPUT_BUCKET,
  's3_key': 'continuous_waveforms/2016/2016_123/CIWCS2_BHE___2016123.ms',
  'decimation_factor': 4
}

print('Invoking lambda function')
response = client.invoke(
        FunctionName=LAMBDA_FUNCTION,
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps(event))
print(response)
