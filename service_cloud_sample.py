#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: service_cloud_sample.py
# Purpose : Submit standalone context insights job to the cloud service
#
# Script description:
# - Create service object
# - Create settings for the job
# - Submit job
# - Monitor job
# ******************************************************************************
from time import sleep

import ccmasterkernel

# Note: You will need to upload a dataset and detector to the cloud before running this example.

# Replace strings here with the ids in the cloud. The context scene must be uploaded after the image collection used and
# the path to the images must be replaced by the id on the cloud in this fashion:
# rds:id_of_the_image_collection

# You can retrieve detectors and datasets here:
# https://communities.bentley.com/products/3d_imaging_and_point_cloud_software/w/wiki/54656/context-insights-detectors-download-page

# The context scene created at the end will point to the dataset in the cloud.

contextSceneId = r"change this string to the ID of the contextScene"  # id of the contextScene in the cloud
photoObjectDetectorId = r"change this string to the ID of the detector"  # id of the detector in the cloud

serviceURL = r"https://api.bentley.com/realitydataanalysis"  # url of the RealityData Analysis Service
iTwinId = r"change this string to your iTwin ID"  # your iTwin ID
jobName = "service cloud sample job"

# create service
service = ccmasterkernel.ServiceCloud(serviceURL, iTwinId)
ret = service.init()
if ret.isError():
    print("There's an error in initialization:", ret.error)
    exit()
print("Service created")

# create settings
settings = ccmasterkernel.O2DJobSettings()
settings.inputs.photos = contextSceneId
settings.inputs.photoObjectDetector = photoObjectDetectorId
settings.outputs.objects2D = "objects2D"
print("Settings created")

# submit job
jobRet = service.submitJob(settings, jobName)
if jobRet.isError():
    print("There's a error in submission:", jobRet.error)
    exit(1)
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
