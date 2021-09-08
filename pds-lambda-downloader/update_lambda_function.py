"""
Upload lambda zip file and reload lambda function.

author: Shang-Lin Chen

"""

# In this example, we have a file named `credentials` in a `.aws` directory.
# e.g.:
# $ cat ~/.aws/credentials
# [lambda-invoker]
# aws_access_key_id = EXAMPLEACCESSKEY
# aws_secret_access_key = EXAMPLESECRETACCESSKEY

import boto3
from settings import *

# Auth to create a Lambda function (credentials are picked up from above .aws/credentials)
session = boto3.Session(profile_name=AWS_PROFILE)

# Upload venv.
print('Uploading venv.zip')
s3_client = session.client('s3')
s3_client.put_object(Key=VENV_FILE, \
                     Bucket=LAMBDA_BUCKET, \
                     Body=open('venv.zip', 'rb') \
                    )
print('Upload complete')

# Make sure Lambda is running in the same region as the HST public dataset
client = session.client('lambda', region_name=AWS_REGION)

# Update the lambda function's code with a new version of venv.zip.
print('Updating lambda function')
response = client.update_function_code(
    FunctionName=LAMBDA_FUNCTION,
    S3Bucket=LAMBDA_BUCKET, # <- this is the bucket which holds your venv.zip file
    S3Key=VENV_FILE,
    Publish=True
)
