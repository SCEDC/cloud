!/usr/bin/env python3

"""
The mseed_referencer class acquires a list of mseed files for event waveforms. 
These waveforms are referenced from a mounted path to the SCEDC Open Data Set (that the user needs to set up).
The waveforms are for events that can be queried by year, month, and magnitude within the class.
"""

import pandas as pd
import boto3

class mseed_referencer():
    def __init__(self, year,month,mag,scedc_path):
        super().__init__()
        self.year=year
        self.month=month
        self.mag=mag
        self.scedc_path=scedc_path
        self.PARENT_DIR = 'event_waveforms'
        self.s3res = boto3.resource('s3')
    
    def get_prefix(self,event_time):
        """ Creates the Open Data Set prefix for an event given the origin time
        as a Pandas timestamp.
        """
        return '{}/{}_{:03d}/'.format(event_time.year, event_time.year, event_time.dayofyear)
    

    def get_events(self):
        """ Get all the events in the SCEDC catalog that occurred in a given year and month and 
        exceed a given magnitude. Return the events in a dataframe.
        """
        catalog_file = '{}_catalog_index.csv'.format(self.year)
        relative_catalog_path='earthquake_catalogs/index/csv/year={}/{}'.format(self.year, catalog_file)
        final_catalog_path=self.scedc_path+'/'+relative_catalog_path
        catalog = pd.read_csv(final_catalog_path)

        if 'ORIGIN_DATETIME' in catalog.columns:
            #make sure the datetime is correct
            catalog=catalog[~catalog.ORIGIN_DATETIME.str.contains(":60", na=False)]

            catalog['eventdate'] = pd.to_datetime(catalog['ORIGIN_DATETIME'])
        elif 'YYYY/MM/DD' in catalog.columns:
            catalog['eventdate'] = pd.to_datetime(catalog['YYYY/MM/DD'])
        
        df = catalog[ (catalog['eventdate'].dt.year==self.year) \
                        & (catalog['eventdate'].dt.month==self.month) \
                        & (catalog['MAG']>=self.mag) ]
        

        if 'PREFIX' not in df.columns:
            df['PREFIX'] = df['eventdate'].apply(self.get_prefix)   
        if 'MS_FILENAME' not in df.columns:
            df['MS_FILENAME'] = df['EVID'].astype(str)+'.ms'
        if 'ORIGIN_DATETIME' not in df.columns:
            df['ORIGIN_DATETIME']=df['YYYY/MM/DD']

        #If there are empty rows in the MS_FILENAME (as is case with 1992), then we will have to add it
        if True in df['MS_FILENAME'].isna().values:
            df['MS_FILENAME'] = df['EVID'].astype(str)+'.ms'

        if 'MS_FILENAME' in df.columns:
            df=df.dropna(subset=['PREFIX', 'MS_FILENAME'])
        download_files = []
        if not df.empty:
            df["total_path"] = self.scedc_path+'/event_waveforms/'+df["PREFIX"] + df["MS_FILENAME"]
            total_paths = df["total_path"].tolist() 
            download_files.extend(total_paths)

        return download_files
