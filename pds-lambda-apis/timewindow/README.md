This Lambda function generates a time window from 
the SCEDC Public Dataset and writes the data to 
S3 or streams to the user through an API.

A sample API is available at the URL 
https://bjn9lwymo7.execute-api.us-west-2.amazonaws.com/request.
To try it, run:
curl -X POST -H "Content-Type: application/json" -d @request.json https://bjn9lwymo7.execute-api.us-west-2.amazonaws.com/request -o CI.WCS2.BHE.sac.

This URL is only available temporarily. You can build your own version of this API
using the instructions in the `pds-lambda-apis` directory.



