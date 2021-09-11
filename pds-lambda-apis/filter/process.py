"""
Lambda function that decimates a miniSEED seismogram from
one S3 bucket and uploads the result to another S3 bucket.

author: Shang-Lin Chen

"""

import os
import boto3
import obspy
import json
import base64
from obspy.core.stream import Stream
from obspy.core import UTCDateTime

formats = {
    'SAC': 'sac',
    'MSEED': 'ms',
}


def filter_waveforms(nscls, infile, fmt):
    st = obspy.read(infile)
    output_files = []

    os.makedirs('/tmp/out', exist_ok=True)

    # if len(nscls) == 0:
    #     for tr in st:
    #         tr.filter('lowpass', freq=1.0, corners=2, zerophase=True)
    #     filename = os.path.basename(infile)
    #     evid, _ = os.path.splitext(filename)
    #     outfile = '/tmp/out/{}.{}'.format(evid, formats[fmt])
    #     print("Writing", outfile)
    #     st.write(outfile, format=fmt)
    #     output_files.append(outfile)

    for nscl in nscls:
        net, sta, chan, loc_orig = nscl.split('.')
        loc = loc_orig.replace('_', '').replace('-', '').replace(' ', '')
        nslc = '.'.join([net, sta, loc, chan])
        st2 = st.select(id=nslc)
        print(st2)
        print('Filtering')
        for tr in st2:
            tr.filter('lowpass', freq=1.0, corners=2, zerophase=True)
        print(st2)
        outfile = '/tmp/out/{}.{}'.format(nslc, formats[fmt])
        print('Writing', outfile)
        st2.write(outfile, format=fmt)
        if not os.path.isfile(outfile):
            print('Writing', outfile, 'failed')
        output_files.append(outfile)

    return output_files


def get_temp_filename(key, start_time):
    basename = os.path.basename(key)
    (filename, ext) = os.path.splitext(basename)
    filename += '_{:02}{:02}{:02}{}'.format(start_time.hour, start_time.minute, start_time.second, ext)
    return '/tmp/' + filename


def process(event, upload=True):
    """ Processes a waveform file from S3 and sends the result to 
    the S3 output bucket.

    :param event: Input parameters to Lambda
    """

    print(event)
    api_gateway = False

    # If the request came from API Gateway, the fields we want are in the 'body'
    # key.
    if 'routeKey' in event:
        api_gateway = True
        print('API Gateway')
        event = json.loads(event['body'])
        print(event)
    
    if 'nscls' in event:
        nscls = event['nscls']
    else:
        nscls = []
    
    bkt_out_name = event['s3_output_bucket']
    bkt_in_name = event['s3_input_bucket']
    evid = event['evid']
    
    session = boto3.Session()
    s3 = boto3.client('s3', region_name='us-west-2')

    filename = '{}.ms'.format(event['evid'])
    key = 'event_waveforms/{0}/{0}_{1:03}/{2}'.format(event['year'], int(event['day']), filename)
    infile = '{}/{}'.format('/tmp', filename)

    # Download file from S3.
    print(bkt_in_name, key)
    s3.download_file(bkt_in_name, key, infile)

    if not os.path.isfile(infile):
        raise Exception('Could not download {} from {} to {}'.format(key, bkt_in_name, infile))

    outfiles = filter_waveforms(nscls, infile, event['format'])
    os.remove(infile)

    #if not os.path.isfile(outfile):
    #    raise Exception('Could not write output file {}'.format(outfile))


    output_key = ''
    print(outfiles)

    output_keys = []
    if upload:
        output_keys = []
        
        for outfile in outfiles:
            print('Uploading {} to {}'.format(outfile, bkt_out_name))
        
            # Get the name of the filename that will be used in S3.
            s3_filename = os.path.basename(outfile)
            output_key = 'filtered/{}/{}'.format(event['evid'], s3_filename)
            output_keys.append(output_key)
            s3.upload_file(outfile, bkt_out_name, output_key)
            os.remove(outfile)

    return { 'output_keys': json.dumps(output_keys) }


def handler(event, context):
    """ Lambda function handler.
    """
    return process(event)
    
