#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: service_job_queue_sample.py
# Purpose : Submit standalone context insights job on premise
#
# Script description:
# - Create service
# - Create settings for the job
# - Submit job
# - Monitor job
# ******************************************************************************
from time import sleep
import os

import ccmasterkernel

# Note: replace paths with your references. You can retrieve detectors and datasets here:
# https://communities.bentley.com/products/3d_imaging_and_point_cloud_software/w/wiki/54656/context-insights-detectors-download-page

# you have to run a CCEngine that points to the job queue at jobQueuePath for this script to work.

jobQueuePath = 'C:/Users/micha/Documents/Bentley/ContextCapture Desktop/Jobs'
contextSceneFolderPath = r"C:\dataset"  # path to contextScene folder
photoObjectDetectorFolderPath = r"C:\detector"  # path to detector folder

jobPrivateDirPath = r"C:\private"  # path to folder where internal files will be saved
objects2DOutputPath = r"C:\production"  # path to where output will be saved

# create service
service = ccmasterkernel.ServiceJobQueue(jobQueuePath)
ret = service.init()
if ret.isError():
    print("There's an error:", ret.error)
    exit()
print("Service created")

# create settings
settings = ccmasterkernel.O2DJobSettings()
settings.inputs.photos = contextSceneFolderPath
settings.inputs.photoObjectDetector = photoObjectDetectorFolderPath
settings.outputs.objects2D = os.path.join(objects2DOutputPath, "objects2D")
print("Settings created")

# submit job
jobRet = service.submitJob(settings, jobPrivateDirPath)
if jobRet.isError():
    print("There's an error in submission:", jobRet.error)
print("Job submitted")
jobId = jobRet.value

# monitor job
progress = 0
status = ccmasterkernel.JobStatusJT.JobStatusJT_Pending
while progress < 100 or status != ccmasterkernel.JobStatusJT.JobStatusJT_Completed:
    jobProgress = service.getJobProgress(jobId)
    if jobProgress.isError():
        print("There's a error in progress retrieval:", jobProgress.error)
        break
    progress = jobProgress.value.progress
    status = jobProgress.value.status
    if status == ccmasterkernel.JobStatusJT.JobStatusJT_Cancelled:
        print("Job cancelled")
        break
    elif status == ccmasterkernel.JobStatusJT.JobStatusJT_Failed:
        print("Job failed")
        break
    print("progress:", progress, "%, status:", status)
    sleep(10)

if status != ccmasterkernel.JobStatusJT.JobStatusJT_Completed:
    print("Job had a problem, we cannot continue the script. Status:", status)
    exit(1)
print("Job finished")
