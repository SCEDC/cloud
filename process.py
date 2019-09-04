import os
import boto3
import obspy
from obspy.core.stream import Stream

def parse_key(key):

    filename = os.path.basename(key)

def decimate(infile, outfile, dec_factor):
    st = obspy.read(infile)
    st_new = Stream()
    for tr in st:
        tr.decimate(factor=dec_factor, strict_length=False)
        st_new.append(tr)
    print(outfile)
    st_new.write(outfile, format='MSEED')

def process(event):
    key = event['s3_key']
    print('Processing {}'.format(key))
    bkt_out_name = event['s3_output_bucket']
    bkt_in_name = event['s3_input_bucket']
    dec_factor = event['decimation_factor']
    print('input bucket:{} output bucket:{} decimation:{}'.format(bkt_in_name, bkt_out_name, dec_factor))
    (year, year_day, filename) = key.split('/')
    (fn, ext) = os.path.splitext(filename)

    if ext != '.ms' and ext != '.mseed':
        print('{} is not a miniSEED file'.format(key))
        return
    
    session = boto3.Session()
    s3 = boto3.client('s3', region_name='us-west-2')

    infile = '/tmp/{}'.format(filename)
    outfile = '/tmp/{}_decimated.ms'.format(fn)
    # Download file from S3.
    s3.download_file(bkt_in_name, key, infile)

    # Decimate the downloaded file and save as outfile.
    decimate(infile, outfile, dec_factor)

    if os.path.isfile(outfile):
        print('Uploading {} to {}'.format(outfile, bkt_out_name))
        s3.upload_file(outfile, bkt_out_name, 'decimated/{}/{}/{}.ms'.format(year, year_day, fn))
        #print(resp)

def handler(event, context):
    process(event)
