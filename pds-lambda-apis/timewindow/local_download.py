#!/usr/bin/env python3

"""
Run the Lambda handler locally without uploading to S3.
"""

from process import *

event = {
  "s3_input_bucket": "scedc-pds",
  "s3_output_bucket": "",
  "nscl": "CI.WCS2.BHE.  ",
  "start_time": "2016-05-02T01:00:00",
  "end_time": "2016-05-02T01:30:00",
  "format": "SAC"
}

process(event, False)
