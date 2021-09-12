# Making Your Lambda Handler Compatible with API Gateway

AWS Lambda receives user inputs in the form of an `event` JSON object. If you're using Python
as your runtime, `event` will be a Python dictionary. 

When your Lambda function is called through an API Gateway, the user's inputs are embeddedin the `body` field
in a larger JSON object with additional keys. The function examples in this directory use the presence of the 
`routeKey` field to determine whether a request comes from API Gateway. The following Python code determines
whether a request is from API Gateway and extracts
the user inputs:

```python
if 'routeKey' in event:
    api_gateway = True
    event = json.loads(event['body'])
```

A complete API Gateway request looks something like:

```
{'version': '2.0', 'routeKey': 'POST /request', 'rawPath': '/request', 'rawQueryString': '', 
 'headers': {'accept': '*/*', 'content-length': '143', 'content-type': 'application/json', 'host': 'api_address.us-west-2.amazonaws.com', 'user-agent': 'curl/7.54.0', 'x-amzn-trace-id': 'Root=1-613c0fb4-662e34ad77fd2c08002b17d0', 'x-forwarded-for': '108.234.225.45', 'x-forwarded-port': '443', 'x-forwarded-proto': 'https'}, 'requestContext': {'accountId': '861771168177', 'apiId': 'api_address', 'domainName': 'api_address.execute-api.us-west-2.amazonaws.com', 'domainPrefix': 'api_address', 'http': {'method': 'POST', 'path': '/request', 'protocol': 'HTTP/1.1', 'sourceIp': 'ip_address', 'userAgent': 'curl/7.54.0'}, 'requestId': 'FedkOhrFPHcEJ2Q=', 'routeKey': 'POST /request', 'stage': '$default', 'time': '11/Sep/2021:02:08:52 +0000', 'timeEpoch': 1631326132410}, 'body': '{"s3_input_bucket": "scedc-pds","nscl": "CI.WCS2.BHE.--","start_time": "2016-05-02T01:00:00","end_time": "2016-05-02T01:30:00","format": "SAC"}', 'isBase64Encoded': False}
```
