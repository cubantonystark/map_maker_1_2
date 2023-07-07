#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: service_cloud_sample_with_upload.py
# Purpose : Submit standalone context insights job to the cloud service
#
# Script description:
# - Create service object
# - Create settings for the job
# - Upload inputs to the cloud
# - Submit job
# - Monitor job
# - Download job output
# ******************************************************************************
from time import sleep
import os

import ccmasterkernel

# Note: replace paths with your references. You can retrieve detectors and datasets here:
# https://communities.bentley.com/products/3d_imaging_and_point_cloud_software/w/wiki/54656/context-insights-detectors-download-page

imageCollectionFolderPath = r"C:\dataset\images"  # path to images folder
contextSceneFolderPath = r"C:\dataset"  # path to contextScene folder
photoObjectDetectorFolderPath = r"C:\detector"  # path to detector folder

outputPath = r"C:\production"  # path to where output will be downloaded

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
settings.inputs.photos = contextSceneFolderPath
settings.inputs.photoObjectDetector = photoObjectDetectorFolderPath
settings.outputs.objects2D = outputPath
print("Settings created")

# create reference table and upload ccimageCollection, contextScene and detector if necessary (not yet on the cloud)
references = ccmasterkernel.ReferenceTable()
referencesPath = os.path.join(outputPath, "test_references_python.txt")
if os.path.isfile(referencesPath):
    print("Loading preexistent references")
    ret = references.load(referencesPath)
    if ret.isError():
        print("Error while loading preexisting references:", ret.error)
        exit(1)

# upload ccimageCollection
if not references.hasLocalPath(imageCollectionFolderPath).value:
    print("No reference to CCimage Collections found, uploading local files to cloud")
    ret = ccmasterkernel.uploadRealityData(iTwinId, imageCollectionFolderPath, "service cloud test image collection", ccmasterkernel.RealityDataType.ImageCollection)
    if ret.isError():
        print("Error in upload:", ret.error)
        exit(1)
    ret = references.addReference(imageCollectionFolderPath, ret.value)
    if ret.isError():
        print("Error adding reference:", ret.error)
        exit(1)

# upload contextScene
if not references.hasLocalPath(contextSceneFolderPath).value:
    print("No reference to ContextScene found, uploading local file to cloud")
    ret = ccmasterkernel.uploadContextScene(iTwinId, contextSceneFolderPath, "service cloud test context scene", references)
    if ret.isError():
        print("Error in upload:", ret.error)
        exit(1)
    ret = references.addReference(contextSceneFolderPath, ret.value)
    if ret.isError():
        print("Error adding reference:", ret.value)
        exit(1)

# upload detector
if not references.hasLocalPath(photoObjectDetectorFolderPath).value:
    print("No reference to detector found, uploading local files to cloud")
    ret = ccmasterkernel.uploadRealityData(iTwinId, photoObjectDetectorFolderPath, "service cloud test detector", ccmasterkernel.RealityDataType.ContextDetector)
    if ret.isError():
        print("Error in upload:", ret.error)
        exit(1)
    ret = references.addReference(photoObjectDetectorFolderPath, ret.value)
    if ret.isError():
        print("Error adding reference:", ret.error)
        exit(1)

# saving references (so we don't need to re-upload afterwards)
ret = references.save(referencesPath)
if ret.isError():
    print("Error saving references:", ret.error)
    exit(1)
print("Checked data upload")

# transform settings in cloud settings (change local paths to ids in the cloud)
cloudSettingsRet = references.convertToCloudSettings(settings)
if cloudSettingsRet.isError():
    print("Error creating cloud settings:", ret.error)
    exit(1)
cloudSettings = cloudSettingsRet.value
print("Cloud settings created")

# submit job
jobRet = service.submitJob(cloudSettings, jobName)
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

# download production
print("Retrieving job settings with output id")
ret = service.getO2DJobSettings(jobId)
if ret.isError():
    print("Error while getting settings:", ret.error)
    exit(1)
finalSettings = ret.value

print("Downloading output")
objects2DId = finalSettings.outputs.objects2D
ret = ccmasterkernel.downloadContextScene(objects2DId, os.path.join(outputPath, "objects2D"), references)
if ret.isError():
    print("Error while downloading output:", ret.error)
    exit(1)
print("Successfully downloaded output")
