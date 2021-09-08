"""
Lambda function that decimates a miniSEED seismogram from
one S3 bucket and uploads the result to another S3 bucket.

author: Shang-Lin Chen

"""

import os
import boto3
import obspy
from obspy.core.stream import Stream

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

    #st.trim(start_time, end_time)

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

def process(event, upload=True):
    """
    Process input parameters and calls decimation function.

    :param event: Input parameters to Lambda
    """

    key = event['s3_key']
    print('Processing {}'.format(key))
    bkt_out_name = event['s3_output_bucket']
    bkt_in_name = event['s3_input_bucket']
    
    #dec_factor = event['decimation_factor']
    
    #print('input bucket:{} output bucket:{} decimation:{}'.format(bkt_in_name, bkt_out_name, dec_factor))
    (wf_dir, year, year_day, filename) = key.split('/')
    (fn, ext) = os.path.splitext(filename)

    session = boto3.Session()
    s3 = boto3.client('s3', region_name='us-west-2')

    infile = '/tmp/{}'.format(filename)
    # Download file from S3.
    s3.download_file(bkt_in_name, key, infile)

    if not os.path.isfile(infile):
        raise Exception('Could not download {} from {} to {}'.format(key, bkt_in_name, infile))

    outfile = write_outfile(infile, fmt=event['format'])

    if not os.path.isfile(outfile):
        raise Exception('Could not write output file {}'.format(outfile))

    output_key = ''
    if upload is True:
        print('Uploading {} to {}'.format(outfile, bkt_out_name))
        output_key = 'download/{}/{}/{}'.format(year, year_day, os.path.basename(outfile))
        s3.upload_file(outfile, bkt_out_name, output_key)
        os.remove(outfile)
        os.remove(infile)
    return output_key

def handler(event, context):
    """ Lambda function handler.
    """
    output_key = process(event)
    return { 'output_key': output_key }

