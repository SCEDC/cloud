"""
Settings for maintaining and running an AWS Lambda function.
"""

AWS_PROFILE = 'schen-gps'           # Profile in .aws/credentials
                                    # that has S3 and Lambda permissions.

AWS_REGION = 'us-west-2'            # AWS region where the lambda function
                                    # is deployed. Should be the same
                                    # region as all S3 buckets.

# AWS IAM role that has Lambda and S3 permissions.
IAM_ROLE = 'arn:aws:iam::205854993909:role/pds-lambda-role'

LAMBDA_FUNCTION = 'SCEDCFunction'   # Name of your lambda function.

LAMBDA_BUCKET = 'schen-lambda-env'  # Name of the S3 bucket that will 
                                    # store a zip file containing 
                                    # the lambda function and environment.

# Description of what your lambda function does.
# This is one of the settings sent to AWS.
LAMBDA_DESCRIPTION = 'Testing Lambda with ObsPy!'

INPUT_BUCKET = 'scedc-pds'          # S3 bucket used as s3_input_bucket.
                                    # This does not need to be modified
                                    # if using the SCEDC Public Data Set.

OUTPUT_BUCKET = 'lambda-decimated'  # Name of the S3 bucket where Lambda
                                    # output will be written.

NCORES = 6   # Number of cores to use for calling Lambda function.

