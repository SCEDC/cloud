# Creating Lambda Functions and APIs

This directory contains code and instructions for creating ObsPy-based
Lambda functions compatible with Amazon API Gateway that use the SCEDC 
Public Dataset. 

Amazon API Gateway places a RESTful interface in front of a Lambda function.
This means you can connect to a web URL to call your Lambda function, using
tools such as curl or any library that can send HTTP requests. Using API 
Gateway also allows your Lambda function to stream data, but note that streaming
data to the Internet incurs data transfer charges. Having your Lambda function
write to S3 instead of stream data remains an option.


## Prerequisites

- Your own AWS account
- [Docker](https://docker.com)
- Python 3
- [`boto3`](https://aws.amazon.com/sdk-for-python/) 
- [`awscli`](https://aws.amazon.com/cli/)

## Setup

In your AWS account:

1. Create an IAM role that has full AmazonS3FullAccess, AWSLambda_FullAccess, and AWSLambdaBasicExecutionRole permissions at https://console.aws.amazon.com/iam/home#/roles. 

2. Create an S3 bucket for holding the zip file your Lambda function will use.

3. Create an S3 bucket for data returned by the Lambda function/API. Some functions also have the option of streaming data directly to your computer.

4. On your computer, your access keys in `.aws/credentials` should have full AmazonS3FullAccess and AWSLambda_FullAccess permissions. Go to https://console.aws.amazon.com/iam/home#/users to create or modify
access keys.

## Creating a Lambda Function

1. Clone the git repo and navigate to this directory.

  ```
  git clone https://github.com/SCEDC/cloud.git
  cd cloud/pds-lambda-apis
  ```

2. Create a Docker image named `lambda-env` using the Dockerfile:
  
  ```
  docker build -t lambda-env .
  ```
This image runs Amazon Linux 2018.03 and has Python 3.7 and ObsPy installed.

3. This directory contains three sample functions. Copy the file `process.py` 
from that function's directory into this directory. For example, to build the
`timewindow` function:
  ```
  cp timewindow/process.py .
  ```

4. Copy `settings_example.py` to `settings.py`, and modify the fields to fit your account. 
 
5. Create the zip file that will be used to create the Lambda function:
```
docker run -v $(pwd):/outputs lambda-env /bin/bash /outputs/build.sh
```
This command starts a Docker container running the lambda-env image, mounts the current directory as `/outputs` in
the container, and runs the script `build.sh`. This script installs ObsPy 1.2.2, NumPy 1.19.5, and SciPy 1.6.0 in
a virtual environment and packages the virtual environment, necessary libraries, and `process.py` in a zip file named
`venv.zip.` 

5. Run `create_lambda_function.py`, which uploads `venv.zip` to the S3 bucket
specified in `LAMBDA_BUCKET` in `settings.py` and creates the Lambda function.

  ```
  python3 create_lambda_function.py
  ```

## Creating an API

In your AWS web console, click on "Services" and select Amazon API Gateway.

## Creating Another Function and API

1. Write a handler for your Lambda function in `process.py`, or copy an existing
`process.py` from one of the example directories.

2. Replace `process.py` in the zip file:

  ```
  zip -r venv.zip process.py
  ```

3. Update `settings.py` or copy an existing `settings.py` to this directory.

4. Then run:

  ```
  python3 create_lambda_function.py
  ```

5. Create an API using API Gateway as in the "Creating an API" section.

