#!/usr/bin/env python3

"""
This code downloads phase picks from the SCEDC Open Data Set for events that occurred 
in a particular year and month and exceed a certain magnitude.
"""

import pandas as pd
import re
import boto3
import botocore

# S3 connection
s3cli = boto3.client('s3')
s3res = boto3.resource('s3')

BUCKET = 'scedc-pds'
TOP_DIR = 'event_phases'

# Function definitions

def get_prefix(event_time):
    """ Creates the Open Data Set prefix for an event given the origin time
    as a Pandas timestamp. This function is only called when the catalog file 
    does not contain the PREFIX column.
    """

    return '{}/{}_{:03d}/'.format(event_time.year, event_time.year, event_time.dayofyear)


def get_phase_filename(evid):
    """ Returns the phase filename for an event, which is evid.phase.
    This function is only called when the catalog file does not contain the
    PHASE_FILENAME column.
    """

    return str(evid) + '.phase'


def get_events(year, month, mag):
    """ Get all the events in the SCEDC catalog that occurred in a given year and month and 
    exceed a given magnitude. Return the events in a dataframe.
    """

    # Get the catalog for the year.
    catalog_file = '{}_catalog_index.csv'.format(year)
    print(catalog_file)
    s3cli.download_file('scedc-pds', 'earthquake_catalogs/index/csv/year={}/{}'.format(year, catalog_file), catalog_file)
    #catalog = pd.read_csv(catalog_file, index_col=False)
    catalog = pd.read_csv(catalog_file)

    # Convert eventdate column from string to Timestamp.
    if 'ORIGIN_DATETIME' in catalog.columns:
        catalog['eventdate'] = pd.to_datetime(catalog['ORIGIN_DATETIME'])
    elif 'YYYY/MM/DD' in catalog.columns:
        catalog['eventdate'] = pd.to_datetime(catalog['YYYY/MM/DD'])
        
    # Get the events that meet the criteria.
    df = catalog[ (catalog['eventdate'].dt.year==year) \
                    & (catalog['eventdate'].dt.month==month) \
                    & (catalog['MAG']>=mag) ]
  
    return df


def download_object(filename):
    """ Downloads a list of files from the SCEDC Open Data Set,
    given their object keys.
    """
    
    # The output file will just be the name of the key without the prefix.
    output_file = filename.split('/')[-1]
    print('Downloading {} to {}.'.format(filename, output_file))
    try:
        s3cli.download_file('scedc-pds', filename, output_file )
    except botocore.exceptions.ClientError as e:
        # If an error occurred, display the messages, but continue on.
        print('Could not download', filename)
        print(e)
        

def download_phases(year, month, mag):
    """ Download waveforms for events in the SCEDC Open Data Set that occurred in
    the given year and month and exceed the given magnitude.
    """

    df = get_events(year, month, mag)
    
    if 'PREFIX' not in df.columns:
        df['PREFIX'] = df['eventdate'].apply(get_prefix) 
    if 'PHASE_FILENAME' not in df.columns:
        df['PHASE_FILENAME'] = df['EVID'].apply(get_phase_filename)
    
    for _, row in df.iterrows():
        download_file = TOP_DIR + '/' + row['PREFIX'] + row['PHASE_FILENAME']
        download_object(download_file)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Download event waveforms from the SCEDC Open Data Set by year, month, and magnitude threshold.')
    parser.add_argument('--year', dest='year', type=int, required=True)
    parser.add_argument('--month', dest='month', type=int, required=True)
    parser.add_argument('--mag', dest='mag', type=float, default=-2)
    args = parser.parse_args()
    download_phases(args.year, args.month, args.mag)


if __name__ == '__main__':
    main()
