# In this example, we have a file named `credentials` in a `.aws` directory.
# e.g.:
# $ cat ~/.aws/credentials
# [lambda-invoker]
# aws_access_key_id = EXAMPLEACCESSKEY
# aws_secret_access_key = EXAMPLESECRETACCESSKEY

import boto3

# Auth to create a Lambda function (credentials are picked up from above .aws/credentials)
session = boto3.Session(profile_name='schen-gps')

# Make sure Lambda is running in the same region as the HST public dataset
client = session.client('lambda', region_name=AWS_REGION)

# Use boto to create a Lambda function.
# Role is created here: https://console.aws.amazon.com/iam/home?region=us-east-1#/home
# The Role needs to have the AWSLambdaFullAccess permission policies attached
# 'your-s3-bucket' is the S3 bucket you've uploaded the `venv.zip` file to
response = client.create_function(
    FunctionName=LAMBDA_FUNCTION,
    Runtime='python3.7',
    Role=IAM_ROLE, # <- Update this with your IAM role name
    Handler='process.handler',
    Code={
        'S3Bucket': LAMBDA_BUCKET, # <- this is the bucket which holds your venv.zip file
        'S3Key': 'venv.zip'
    },
    Description=LAMBDA_DESCRIPTION,
    Timeout=300,
    MemorySize=1024,
    Publish=True
)
