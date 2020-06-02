###
#
# Fetch SCEDC PDS continuous miniseed data using SCEDC FDSN availability web service as input
# inputs :
# 1. A file containing output of query end point of https://service.scedc.caltech.edu/fdsnws/availability/1/
#    with format=request
# 2. A directory to store downloaded miniseed files. Optional. If not specified, current directory is used.
# 3. Number of processes to use for downloads. Optional. If not specified, defaults to 1.
#
# outputs :
# 1. Downloaded miniseed files from s3://scedc-pds/continuous_waveforms
# 2. A text file containing s3 locations of downloaded files.
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
from math import ceil
from datetime import datetime, timedelta
from multiprocessing import Process, Queue, cpu_count
import time


#collect all files to download in this list                                                                          
#pds = [[s3_file, local_file, True], [s3_file2, local_file2, True]...[s3_fileN, local_fileN, True]]          
pds = []
time2download = 0
bytes_downloaded = 0

def Main():
    global pds
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
    parser.add_argument("-t", dest="processes", type=int, default=1, help="Number of processes to run the download with. For e.g. -t 2 will divide the requests between 2 processes. Default is 1.")
    args = parser.parse_args()

    if not os.path.exists(args.infile):
        print ("%s does not exist. Exiting..." %args.infile)
        return
        
    infile = args.infile
    outdir = args.outdir
    num_processes = args.processes

    if not args.outdir:        
        print ("no output location provided, use current dir")
        outdir = os.path.dirname(os.path.abspath(__file__))

    try:
        #pds = {} #collect all files to download in this dictionary
        #read input file
        with open(infile, 'r') as fp:
            alllines = fp.readlines()

        fp = open(pds_files, 'w')
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
                
                fp.write(pds_miniseed + '\n')
                ms_file = os.path.join(outdir, ms_file) #download destination, ms_file is <net><sta><chan><loc>_YYYYJJJ.ms

                if [pds_miniseed, ms_file] not in pds:
                    pds.append([pds_miniseed, ms_file])
                date += timedelta(days=1)
        
        fp.close()
        
        #now copy the text file to outdir
        if outdir.find("s3://") != -1:
            cmd = ['aws','s3','cp',pds_files, outdir]
            subprocess.call(cmd)
        else:
            shutil.move(pds_files, os.path.join(outdir, pds_files))

        [item.append(True) for item in pds]

        print("Starting download from pds for", len(pds), "requests...")
        step  = ceil(len(pds)/num_processes)
        if len(pds) < num_processes:
            print("The number of requests (", len(pds),") < number of requested processes (", num_processes,"), using all available cores (",cpu_count(),") instead")
            num_processes = cpu_count()
        
        print ("Dividing requests between", num_processes, "process(es)")
        
        start_index = 0
        end_index   = step
        procs = []       #store process is here
        output = Queue() #store per process bytes downloaded
        output_duration = Queue() #store per process duration to download

        for i in range(0, num_processes):
            
            procs.append(Process(target=DownloadFromPDS, args=(start_index,end_index,output, output_duration)))
            procs[i].start()

            start_index += step
            end_index += step
        
        while 1:   
            alive = 0
            for proc in procs:
                if proc.is_alive():
                    alive+= 1
            if alive <= num_processes:
                pass
            if not alive:
                break

        total = 0
        total_duration = 0
        qsize = 0
        
        while not output.empty():
            total += output.get()
            total_duration += output_duration.get()
            qsize += 1 #we do this instead of using Queue.qsize() as Queue.qsize() is not supported on mac

        #using qsize instead of num_processes here as sometimes some processes have no download stats (??) 
        print ("TOTAL bytes downloaded : ", total, \
               "\nAVG time to download per process : ", total_duration/float(qsize), '\n')
        
    except:
        evalue, etype, etraceback = sys.exc_info()
        traceback.print_exception(evalue, etype, etraceback)


def DownloadFromPDS(start, end, output, output_duration):
    global pds

    bytes_per_process = 0
    download_start = datetime.now()

    try:
        for item in pds[start:end]:

            pds_miniseed = item[0]             
            ms_file = item[1]
            cmd = ['aws','s3','cp', '--quiet', pds_miniseed, ms_file]
            print ('[', os.getpid(), ']', cmd)

            subprocess.call(cmd)
            if os.path.exists(ms_file):
                 bytes_per_process += os.stat(ms_file).st_size
    except:
        evalue, etype, etraceback = sys.exc_info()
        traceback.print_exception(evalue, etype, etraceback)
    
    td = datetime.now() - download_start

    time2download = td.seconds
    if time2download > 0:
        sys.stdout.flush()
        
        if time2download < 60:
            print ('[',os.getpid(), '] Time to download per process is ', time2download, 'seconds')
        else:
            print ('[', os.getpid(), '] Time to download per process is ', time2download/60.0, 'minutes')
        print ('[',os.getpid(), "] MB downloaded    = ", bytes_per_process/(1024.0 * 1024.0))
        print ('[',os.getpid(), "] Rate of download = ", (bytes_per_process/(1024.0 * 1024.0))/time2download, " MB/sec")
        print ("\n")    
    
    output.put(bytes_per_process)
    output_duration.put(time2download)

if __name__ == "__main__":
    major, minor, micro, releaselevel, serial = sys.version_info
    if major < 3:
        print ("\nPython version used is %s.%s.%s. Please use Python 3.6 or higher\n" %(major, minor, micro))
        sys.exit()
    Main()
