# Example script to download continuous waveform data from SCEDC Public Data Set

This is an example that shows the user how to download continuous data from the SCEDC PDS by querying the SCEDC's FDSN availability web service. The web service has an option to produce output for making POST requests. This is used as the input to the example. The output is a set of miniseed files and a text file listing the PDS location of all downloaded files. The location to download can be a local directory or an s3 bucket.

## Prerequisites
  * Your own aws account
  * Python >= 3.6 (Currently, tested only on Python 3.6)
  * aws command line client

## Getting availability information

Use the FDSN availability web service **query** endpoint to get information about data availability. For more information and help, please see https://service.scedc.caltech.edu/fdsnws/availability/1/

The example below retrieves all CI stations that start with the letter B and have BHZ channel data between 2019-03-04 and 2019-03-05. format=request produces output in HTTP POST format.  

``
wget -O avail.txt "https://service.scedc.caltech.edu/fdsnws/availability/1/query?net=CI&sta=B*&cha=BHZ&loc=--&start=2019-03-04T00:00:00&end=2019-03-05T00:00:00&format=request&nodata=404"
``
  
*avail.txt* looks like this
```
CI BAK -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BAR -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BBR -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BBS -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BC3 -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BCW -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BEL -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BFS -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
CI BHP -- BHZ 2019-03-04T00:00:00.000000Z 2019-03-05T00:00:00.000000Z
...

```


## Usage  
```
python3 fetch_continuous_data.py --help
usage: fetch_continuous_data.py [-h] --infile INFILE [--outdir OUTDIR]
                                [-t PROCESSES]

Fetch continuous miniseed data from s3://scedc-pds using SCEDC FDSN availability web service as input.
The SCEDC FDSN availability web service's query end point with format=request may be used to generate the input to this program.
For e.g.
wget -O avail.out "https://service.scedc.caltech.edu/fdsnws/availability/1/query?net=CI&sta=B*&cha=BHZ&loc=--&start=2019-03-04T00:00:00&end=2019-03-05T00:00:00&format=request&nodata=404"
Then, use avail.out as input to this program using --infile

Downloads are made from s3://scedc-pds/continuous_waveforms/

More information regarding the webservice at https://service.scedc.caltech.edu/fdsnws/availability/1/

1. A folder containing : 
   a. Downloaded miniseed files 
   b. A text file containing s3 locations of downloaded files.
2. On the console:  A per process as well as comprehensive summary of time taken to download in minutes, megabytes downloaded and rate of download

optional arguments:
  -h, --help       show this help message and exit
  --infile INFILE  Input file containing requests
  --outdir OUTDIR  Folder where downloaded files will be stored. It can be a
                   local folder or s3 bucket. Default is directory where the
                   program is located. Also contains a text file listing s3
                   locations of downloaded files
  -t PROCESSES     Number of processes to run the download with. For e.g. -t 2
                   will divide the requests between 2 processes. Default is 1.
```
  
Example usage  

```
python3 fetch_continuous_data.py --infile avail.txt --outdir /tmp  

python3 fetch_continuous_data.py -t 8 --infile avail.txt --outdir /tmp  

python3 fetch_continuous_data.py --infile avail.txt --outdir s3://mybucket/myfolder/
```
  
## Output  

The outputs are  
  * A set of miniSEED files satisfying the input requests. All downloaded files are a day long.
  * A text file named *scedc-pds-files.txt* containing the pds location of downloaded files.
  
  

 



