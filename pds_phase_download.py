#!/usr/bin/env python3

"""
This code downloads phase picks from the SCEDC Open Data Set for events that occurred 
in a particular year and month and exceed a certain magnitude.
"""

import pandas as pd
import re
import boto3

# S3 connection
s3cli = boto3.client('s3')
s3res = boto3.resource('s3')

# Function definitions

def get_prefix(event_time):
    """ Creates the Open Data Set prefix for an event given the origin time
    as a Pandas timestamp.
    """
    return 'event_phases/{}/{}_{}/'.format(event_time.year, event_time.year, event_time.dayofyear)


def get_events(year, month, mag):
    """ Get all the events in the SCEDC catalog that occurred in a given year and month and 
    exceed a given magnitude. Return the events in a dataframe.
    """
    # Get the catalog for the year.
    catalog_file = '{}.catalog.csv'.format(year)
    print(catalog_file)
    s3cli.download_file('scedc-pds', 'earthquake_catalogs/index/csv/year={}/{}'.format(year, catalog_file), catalog_file)
    #catalog = pd.read_csv(catalog_file, index_col=False)
    catalog = pd.read_csv(catalog_file)

    # Convert eventdate column from string to Timestamp.
    catalog['eventdate'] = pd.to_datetime(catalog['YYYY/MM/DD'])
    # Get the events that meet the criteria.
    df = catalog[ (catalog['eventdate'].dt.year==year) \
                    & (catalog['eventdate'].dt.month==month) \
                    & (catalog['MAG']>=mag) ]
  
    return df


def download_objects(download_files):
    """ Downloads a list of files from the SCEDC Open Data Set,
    given their object keys.
    """
    for f in download_files:
        # The output file will just be the name of the key without the prefix.
        output_file = f.split('/')[-1]
        print('Downloading {} to {}.'.format(f, output_file))
        s3cli.download_file('scedc-pds', f, output_file )
        
        
def list_objects(evid, prefix):
    """ Returns a list of object names that match an event,
    given the event ID and the Open Data Set prefix of the event.    
    """
    regex = re.compile('.*\/{}.*$'.format(evid))
    obj_names = []
    for obj in s3res.Bucket('scedc-pds').objects.filter(Prefix=prefix):
        if regex.match(obj.key):
            print('Match {}'.format(obj.key))
            obj_names.append(obj.key)
            
    return obj_names

def download_phases(year, month, mag):
    """ Download waveforms for events in the SCEDC Open Data Set that occurred in
    the given year and month and exceed the given magnitude.
    """
    df = get_events(year, month, mag)
    # Determine the S3 prefix for each event.
    df['prefix'] = df['eventdate'].apply(get_prefix)       
    download_files = []
    for _, row in df[['EVID', 'prefix']].iterrows():
        download_files += list_objects(row['EVID'], row['prefix'])
    download_objects(download_files)


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
