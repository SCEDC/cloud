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

def write_outfile(infile, start_time=None, end_time=None, dec_factor=1, fmt='MSEED'):
    """
    Write an output file in the desired format.
    :param infile: Name of the input file
    :param outfile: Name of the output file
    :param dec_factor: Decimation factor
    """
    
    print('Reading', infile)
    st = obspy.read(infile)

    if start_time and end_time:
        st.trim(start_time, end_time)

    #st_new = Stream()
    # Decimate each trace in the stream.
    if dec_factor > 1:
        print('Decimating traces')
        for tr in st:
            tr.decimate(factor=dec_factor, strict_length=False, no_filter=True)
            #st_new.append(tr)
        # Write the resulting stream to disk.

    input_filename, _ = os.path.splitext(infile)

    if fmt in formats:
        outfile = "{}.{}".format(input_filename, formats[fmt])
        print('Writing', outfile)
        st.write(outfile, format=fmt)
    else:
        raise Exception('Unknown format')
    return outfile


def get_time_window(event):
    """ Returns a time window as a pair of obspy.core.UTCDateTime objects,
    given the Lambda input event. The start_time and end_time fields are expected
    to be present as ISO8601:2004 strings.
    """
    start_time = None
    end_time = None

    if 'start_time' in event:
        start_time = UTCDateTime(event['start_time'])
    else:
        raise Exception('No start time set')
    if 'end_time' in event:
        end_time = UTCDateTime(event['end_time'])
    
    return start_time, end_time


def get_input_key(nscl, start_time):
    """ Returns the key of the object in the SCEDC Public Dataset bucket
    that corresponds to a NSCL string and start time.
    """
    net, sta, chan, loc = nscl.split('.')

    # '-' can be used to stand for spaces in the location code.
    # Convert both '-' and actual spaces to '_' because that is used 
    # in the key names.
    loc = loc.replace('-', '_').replace(' ', '_')
    
    key = 'continuous_waveforms/{0}/{0}_{1:03}/{2}{3}_{4}{5}_{0}{1:03}.ms'.format(start_time.year, start_time.julday, net, sta, chan, loc)
    return key


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
    
    nscl = event['nscl']

    if 's3_output_bucket' in event:
        bkt_out_name = event['s3_output_bucket']
    else:
        upload = False

    bkt_in_name = event['s3_input_bucket']
    
    start_time, end_time = get_time_window(event)
    if start_time is None or end_time is None:
        raise Exception("Missing start_time or end_time.")
    if start_time.year != end_time.year or start_time.julday != end_time.julday:
        raise Exception("Time windows must start and end within the same day.")

    #dec_factor = event['decimation_factor']
    
    #print('input bucket:{} output bucket:{} decimation:{}'.format(bkt_in_name, bkt_out_name, dec_factor))
    #(wf_dir, year, year_day, filename) = key.split('/')
    #(fn, ext) = os.path.splitext(filename)

    session = boto3.Session()
    s3 = boto3.client('s3', region_name='us-west-2')

    key = get_input_key(nscl, start_time)
    infile = get_temp_filename(key, start_time) 

    print(key, infile)

    # Download file from S3.
    s3.download_file(bkt_in_name, key, infile)

    if not os.path.isfile(infile):
        raise Exception('Could not download {} from {} to {}'.format(key, bkt_in_name, infile))

    outfile = write_outfile(infile, start_time, end_time, fmt=event['format'])

    if not os.path.isfile(outfile):
        raise Exception('Could not write output file {}'.format(outfile))

    output_key = ''
    if upload:
        print('Uploading {} to {}'.format(outfile, bkt_out_name))
        output_key = 'data/{}'.format(os.path.basename(outfile))
        s3.upload_file(outfile, bkt_out_name, output_key)
   
    os.remove(infile)
    outfile_bytes = open(outfile, 'rb').read()
    
    if upload:
        os.remove(outfile)
    
    if api_gateway:
        return { 
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/octet-stream'},
            'body': base64.b64encode(outfile_bytes).decode("utf-8"),
            'isBase64Encoded': True
        }
    else:
        return { 'output_key': output_key }

def handler(event, context):
    """ Lambda function handler.
    """
    return process(event)
    
