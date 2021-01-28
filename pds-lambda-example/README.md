This project is a Lambda function that uses ObsPy to
decimate seismograms from the SCEDC Open Data Set by a factor of four and 
writes the output to another S3 bucket in the user's own account.

**Prerequisites**

- Your own AWS account
- [Docker](https://docker.com)
- Python 3
- [`boto3`](https://aws.amazon.com/sdk-for-python/) 
- [`awscli`](https://aws.amazon.com/cli/)

**Setup**

In your AWS account:

1. Create an IAM role that has full AmazonS3FullAccess, AWSLambda_FullAccess, and AWSLambdaBasicExecutionRole permissions at https://console.aws.amazon.com/iam/home#/roles.

2. Create two S3 buckets in the US-West-2 region at https://s3.console.aws.amazon.com/s3/home. One of these buckets will
hold the zip file for creating the Lambda function, and the other will hold the
decimated data. The US-West-2 region is necessary because the SCEDC Open Data Set is located in US-West-2.

On your computer, your access keys in `.aws/credentials` should have full AmazonS3FullAccess and AWSLambda_FullAccess permissions. Go to https://console.aws.amazon.com/iam/home#/users to create or modify
access keys.

**Creating the Lambda Function**

1. Clone the git repo and `cd` to the `pds-lambda-example` directory.

```
git clone https://github.com/SCEDC/cloud.git
cd cloud/pds-lambda-example
```

2. Create a Docker image named `lambda-env` using the Dockerfile:
  ```
  docker build -t lambda-env .
  ```
This image runs Amazon Linux 2018.03 and has Python 3.7 and the yum packages required by ObsPy installed.

3. Create the zip file, `venv.zip`, that will be used to create the Lambda function:
```
docker run -v $(pwd):/outputs lambda-env /bin/bash /outputs/build.sh
```
This command start a Docker container running the lambda-env image, mounts the current directory as `/outputs` in
the container, and runs the script `build.sh`. This script installs ObsPy 1.2.2, NumPy 1.19.5, and SciPy 1.6.0 in
a virtual environment and packages the virtual environment, necessary libraries, and `process.py` in a zip file named
`venv.zip.` `process.py` contains the code of the Lambda function.

4. Copy `settings_example.py` to `settings.py`, and update the variables in `settings.py` with values 
that make sense for your AWS account. These variables might need to be modified:
- `AWS_PROFILE` - If your are not using a default profile in `.aws/credentials`, change this value to 
the profile name.
- `IAM_ROLE` - Set this to your own IAM role.
- `LAMBDA_FUNCTION` - Set this to the name of the Lambda function you want to create.
- `LAMBDA_BUCKET` - Set this to the name of the S3 bucket that will contain `venv.zip`. 
- `OUTPUT_BUCKET` - Set this to the name of the S3 bucket that will contain your decimated output. 
- `NCORES` - Set this to the number of cores on your local computer that you want to use to call the Lambda function if you run `decimate.py`.

5. Run `create_lambda_function.py`, which uploads `venv.zip` to `LAMBDA_BUCKET` and creates the Lambda function.
```
python3 create_lambda_function.py
```

6. Run `run_lambda.py` to call the Lambda function on one seismogram.
```
python3 run_lambda.py
```
You should see the decimated
file appear in your output S3 bucket as `decimated/2016/2016_123/CIWCS2_BHE___2016123.ms`.

**Decimating Multiple Seismograms**

`decimate.py` will call the Lambda function on each seismogram in a list of seismograms, using the `concurrent.futures` module to call Lambda in parallel. The value of `NCORES` in `settings.py` determines the number of 
parallel threads. 

Example:  Create a file named `seismograms.txt` that contains the following keys from the Open Data Set:
```
continuous_waveforms/2016/2016_001/AZBZN__BHE___2016001.ms
continuous_waveforms/2016/2016_001/AZBZN__BHN___2016001.ms
continuous_waveforms/2016/2016_001/AZBZN__BHZ___2016001.ms
continuous_waveforms/2016/2016_001/AZCPE__BHE___2016001.ms
``` 
Run:
```
python3 decimate.py seismograms.txt
```
to produce decimated waveforms in your S3 output bucket.

You can use the shell script `make_listings` 
to help you generate a list of seismograms. For example, to generate a list of seismograms from BH channels from January 1 to 31, 2016, and store
them in the file `jan2016.txt`, run:
```
./make_listings 2016 1 31 >jan2016.txt
```
Decimate the seismograms in `jan2016.txt` by running:
```
python3 decimate.py jan2016.txt
```

You can also use the `awscli` module to explore the Public Data Set:
```
aws s3 ls s3://scedc-pds/continuous_waveforms/
```
and determine which seismograms you want to process.

**Updating the Lambda Function**

If you need to modify the Lambda function but don't need additional libraries,
update `process.py` and run:
```
zip -r venv.zip process.py
```
to replace the version of `process.py` in `venv.zip`.

Then run:
```
python3 update_lambda_function.py
```
to upload the new version of venv.zip and reload the Lambda
function.
