"""
Lambda function that decimates a miniSEED seismogram from
one S3 bucket and uploads the result to another S3 bucket.
"""

import os
import boto3
import obspy
from obspy.core.stream import Stream


def decimate(infile, outfile, dec_factor):
    """
    Runs ObsPy's decimate function on the traces
    in an input seismogram.

    :param infile: Name of the input file
    :param outfile: Name of the output file
    :param dec_factor: Decimation factor
    """
    st = obspy.read(infile)
    st_new = Stream()
    # Decimate each trace in the stream.
    for tr in st:
        tr.decimate(factor=dec_factor, strict_length=False)
        st_new.append(tr)
    print(outfile)
    # Write the resulting stream to disk.
    st_new.write(outfile, format='MSEED')


def process(event):
    """
    Process input parameters and calls decimation function.

    :param event: Input parameters to Lambda
    """

    key = event['s3_key']
    print('Processing {}'.format(key))
    bkt_out_name = event['s3_output_bucket']
    bkt_in_name = event['s3_input_bucket']
    dec_factor = event['decimation_factor']
    print('input bucket:{} output bucket:{} decimation:{}'.format(bkt_in_name, bkt_out_name, dec_factor))
    (year, year_day, filename) = key.split('/')
    
    session = boto3.Session()
    s3 = boto3.client('s3', region_name='us-west-2')

    infile = '/tmp/{}'.format(filename)
    outfile = '/tmp/{}_decimated.ms'.format(fn)
    # Download file from S3.
    s3.download_file(bkt_in_name, key, infile)

    if not os.path.isfile(infile):
        raise Exception('Could not download {} from {} to {}'.format(key, bkt_in_name, infile)

    decimate(infile, outfile, dec_factor)

    if not os.path.isfile(outfile):
        raise Exception('Could not write output file {}'.format(outfile))

    print('Uploading {} to {}'.format(outfile, bkt_out_name))
    s3.upload_file(outfile, bkt_out_name, 'decimated/{}/{}/{}.ms'.format(year, year_day, fn))
    os.remove(outfile)
    os.remove(infile)


def handler(event, context):
    """ Lambda function handler.
    """
    try:
        process(event)
    except Exception as error:
        print(error)
        return {'message': str(error)}
