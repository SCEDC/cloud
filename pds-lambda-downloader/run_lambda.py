#!/usr/bin/env python3

"""
run_lambda.py runs the lambda function on one seismogram.
"""

import boto3
import json
from settings import *

session = boto3.Session(profile_name=AWS_PROFILE)
client = session.client('lambda', region_name=AWS_REGION)

event = {
  "s3_input_bucket": INPUT_BUCKET,
  "s3_output_bucket": OUTPUT_BUCKET,
  "nscl": "CI.WCS2.BHE.  ",
  "start_time": "2016/05/02T01:00:00",
  "end_time": "2016/05/02T01:30:00",
  "format": "SAC"
}

print('Invoking lambda function')
response = client.invoke(
        FunctionName=LAMBDA_FUNCTION,
        InvocationType='RequestResponse',
        LogType='Tail',
        Payload=json.dumps(event))
#print(response)
print(response['Payload'].read())
