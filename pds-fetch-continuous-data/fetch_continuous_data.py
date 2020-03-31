###
#
# Fetch SCEDC PDS continuous miniseed data using SCEDC FDSN availability web service as input
# inputs :
# 1. A file containing output of query end point of https://service.scedc.caltech.edu/fdsnws/availability/1/
#    with format=request
# 2. A directory to store downloaded miniseed files. Optional. If not specified, current directory is used.
#
# outputs :
# 1. Downloaded miniseed files from s3://scedc-pds/continuous_waveforms
# 2. A text file containing s3 locations of  downloaded files.
#
# pre-requisites:
# Python3, aws command line client
#
###

import argparse
import textwrap
import sys
import os
import shutil
import traceback
import subprocess
from datetime import datetime, timedelta


def Main():

    infile = None
    outdir = None
    pds_files = 'scedc-pds-files.txt'
    
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                     Fetch continuous miniseed data from s3://scedc-pds using SCEDC FDSN availability web service as input.
                                     The SCEDC FDSN availability web service's query end point with format=request may be used to generate the input to this program.
                                     For e.g.
                                     wget -O avail.out "https://service.scedc.caltech.edu/fdsnws/availability/1/query?net=CI&sta=B*&cha=BHZ&loc=--&start=2019-03-04T00:00:00&end=2019-03-05T00:00:00&format=request&nodata=404"
                                     Then, use avail.out as input to this program using --infile

                                     Downloads are made from s3://scedc-pds/continuous_waveforms/

                                     More information regarding the webservice at https://service.scedc.caltech.edu/fdsnws/availability/1/
                                     '''))
    parser.add_argument("--infile", required=True, help="Input file containing requests")
    parser.add_argument("--outdir", default=os.path.dirname(os.path.abspath(__file__)), help="Location where downloaded files will be stored. It can be a local folder or s3 bucket. Default is directory where the program is located.")
    args = parser.parse_args()

    if not os.path.exists(args.infile):
        print ("%s does not exist. Exiting..." %args.infile)
        return
        
    infile = args.infile
    outdir = args.outdir

    if not args.outdir:        
        print ("no output location provided, use current dir")
        outdir = os.path.dirname(os.path.abspath(__file__))

    try:
        pds = {} #collect all files to download in this dictionary
        #read input file
        with open(infile, 'r') as fp:
            alllines = fp.readlines()

        #process each line in the input file
        for line in alllines:
            net, sta, loc, chan, start, end = line.split(' ')

            pds_start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S.%fZ')
            pds_end = datetime.strptime(end.strip(), '%Y-%m-%dT%H:%M:%S.%fZ')
            
            diff = pds_end - pds_start
            if diff.days ==1 and diff.seconds == 0:
                pds_end = pds_start

            date = pds_start #initialize loop variable to pds_start
            #process all dates from pds_start to pds_end
            while date <= pds_end:

                pds_miniseed = "s3://scedc-pds/continuous_waveforms/%s/%s/" %(date.year, date.strftime("%Y_%j"))
                ms_file = "{:s}{:_<5}{:s}{:s}_{:s}.ms".format(net, sta, chan, loc.replace('-','_'), date.strftime("%Y%j"))            
                pds_miniseed += ms_file #download source, pds_miniseed is now s3://scedc-pds/continuous_waveforms/<year>/<year_jjj>/<net><sta><chan><loc>_YYYYJJJ.ms
                
                ms_file = os.path.join(outdir, ms_file) #download destination, ms_file is <net><sta><chan><loc>_YYYYJJJ.ms
                key = date.strftime("%Y_%j")
                if key not in pds:
                    pds[key] = []
                if pds_miniseed not in pds[key]:
                    pds[key].append(pds_miniseed)
                    pds[key].append(ms_file)
                date += timedelta(days=1)

        print("Starting download from pds...")
        start = datetime.now()
        fp = open(pds_files,'w') #file containing list of pds files being downloaded, scedc-pds-file.txt
        for key in pds:
            for i in range(0, len(pds[key]), 2):
                
                pds_miniseed = pds[key][i]
                ms_file = pds[key][i+1]

                fp.write(pds_miniseed + '\n') #write miniseed filename to scedc-pds-files.txt

                #perform the download
                cmd = ['aws','s3','cp',pds_miniseed, ms_file]
            
                subprocess.call(cmd)
        fp.close()

        print("Download complete in ",datetime.now() -start)

        #now copy the text file to outdir
        if outdir.find("s3://") != -1:
            cmd = ['aws','s3','cp', pds_files, outdir]
            subprocess.call(cmd)
        else:
            shutil.move(pds_files, os.path.join(outdir, pds_files))
    except:
        evalue, etype, etraceback = sys.exc_info()
        traceback.print_exception(evalue, etype, etraceback)


if __name__ == "__main__":
    Main()
