The scedc-lambda project is an example Lambda function that uses ObsPy to
decimate seismograms from the SCEDC Open Data Set by a factor of four and 
writes the output to another S3 bucket in the user's own account.

**Prerequisites**

- Your own AWS account
- Docker
- Python 3
- boto3 module for Python
- awscli module for Python

**AWS Setup**

In your AWS account:

1. Create a new IAM role that has full S3 and Lambda permissions.

2. Create two S3 buckets in the US-West-2 region. One of these buckets will
hold the zip file for the Lambda function, and the other will hold the
decimated data.

On your computer make sure you have AWS programmatic access keys that have
full Lambda permissions.

**Creating the Lambda Function**

1. Run this command:
  docker build -t lambda-env .
to create a Docker image called lambda-env that runs
amazonlinux:2018.03 and has Python 3.7 installed.

2. Run this command:
  docker run -v $(pwd):/outputs lambda-env /bin/bash /outputs/build.sh
to create a zip file named venv.zip. The script build.sh installs numpy and Obspy
in a virtual environment in a Docker container and zips the virtual environment
along with process.py, which contains the lambda function.

3. Update settings.py with the names of your AWS profile in .aws/credentials,
the name of your IAM role, the name you want to use for your lambda function, 
and the S3 buckets you created. You do not need to change INPUT_BUCKET or AWS_REGION 
if you're using the SCEDC Open Data Set. NCORES should be set to the number of
CPU cores you want to use on your computer when calling the lambda function.

3. Upload venv.zip to the S3 bucket defined in LAMBDA_BUCKET in settings.py.
  aws s3 cp venv.zip s3://my-lambda-env-bucket/

4. Run:
  python create_lambda_function.py
to create the Lambda function.

5. Run:
  python run_lambda.py
to call the lambda function on one seismogram. You should see the decimated
file appear in your output S3 bucket as decimated/2016/2016_123/CIWCS2_BHE___2016123.ms.

* Running Decimation *

decimate.py will call the Lambda function on a list of seismograms by key. Set the 
values of NCORES in settings.py to how many local CPU cores you want to use for
sending Lambda function calls, and run:
  python decimate.py filename_of_seismogram_list

The list should contain the full path of each seismogram, one per line. Below is a sample listing:

2016/2016_001/AZBZN__BHE___2016001.ms
2016/2016_001/AZBZN__BHN___2016001.ms
2016/2016_001/AZBZN__BHZ___2016001.ms
2016/2016_001/AZCPE__BHE___2016001.ms

You can generate listings by using the "aws s3 ls" command.

**Updating the Lambda Function**

If you need to modify the Lambda function, make your changes in process.py and replace
process.py in the zip file by running:
  zip -r venv.zip process.py
This only replaces process.py, so you don't need to re-run the docker command to
create a new zip file. 

Then run:
  python update_lambda_function.py
which will automatically upload the new version of venv.zip and reload the Lambda
function.
