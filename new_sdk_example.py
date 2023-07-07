#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
import os
import ccmasterkernel
import time

rdas_url = "https://qa-connect-contextinsights.bentley.com/api/v1"
project_id = "ad14b27c-91ea-4492-9433-1e2d6903b5e4"

input_path = r"Q:\Analyze\ContextInsightsQA_デテクター"
output_path = r"D:\Standalone\outputs"

CLOUD = True

if CLOUD:
    service = ccmasterkernel.ServiceCloud(rdas_url, project_id)
else:
    service = ccmasterkernel.ServiceJobQueue(r"C:\Projects\InternalJobs")
    
ret = service.init()
if ret.isError():
    print("Error in init:", ret.error)
    exit(1)
    
settings = ccmasterkernel.O2DJobSettings()
settings.inputs.photos = os.path.join(input_path, r"DataSets\Motos\Photos")
settings.inputs.photoObjectDetector = os.path.join(input_path, r"Detectors\PhotoObjectDetector\Coco2017_v1")
settings.outputs.objects2D = os.path.join(output_path, r"O2D_motos_バイク\objects2D")

print("Created settings")
    
if CLOUD:
    references = ccmasterkernel.ReferenceTable()
    referencesPath = os.path.join(output_path, "test_references_python.txt")
    if os.path.isfile(referencesPath):
        ret = references.load(referencesPath)
        if ret.isError():
            print("Error in load references:", ret.error)
            exit(1)
        
    photosImagePath = r"Q:\Analyze\ContextInsightsQA_デテクター\DataSets\Motos\Images_バイク"
    if not references.hasLocalPath(photosImagePath).value:
        ret = ccmasterkernel.uploadRealityData(project_id, photosImagePath, "TestMotoPhotosPy", ccmasterkernel.RealityDataType.ImageCollection)
        if ret.isError():
            print("Error in upload:", ret.error)
            exit(1)
        ret = references.addReference(photosImagePath, ret.value)
        if ret.isError():
            print("Error adding reference:", ret.error)
            exit(1)
        
    if not references.hasLocalPath(settings.inputs.photoObjectDetector).value:
        ret = ccmasterkernel.uploadRealityData(project_id, settings.inputs.photoObjectDetector, "TestCocoDetectorPy", ccmasterkernel.RealityDataType.ContextDetector)
        if ret.isError():
            print("Error in upload:", ret.error)
            exit(1)
        ret = references.addReference(settings.inputs.photoObjectDetector, ret.value)
        if ret.isError():
            print("Error adding reference:", ret.error)
            exit(1)
        
    if not references.hasLocalPath(settings.inputs.photos).value:
        ret = ccmasterkernel.uploadContextScene(project_id, settings.inputs.photos, "TestMotoScenePy", references)
        if ret.isError():
            print("Error in upload:", ret.error)
            exit(1)
        ret = references.addReference(settings.inputs.photos, ret.value)
        if ret.isError():
            print("Error adding reference:", ret.error)
            exit(1)
            
    ret = references.save(referencesPath)
    if ret.isError():
        print("Error saving reference:", ret.error)
        exit(1)
    

    print("Checked data upload")

if CLOUD:
    ret = references.convertToCloudSettings(settings)
    if ret.isError():
        print("Error in convert:", ret.error)
        exit(1)
    settings = ret.value
    ret = service.submitJob(settings, "O2D_motos_バイク_TestPy")
else:
    ret = service.submitJob(settings, os.path.join(output_path, "O2D_motos_バイク", "private"))
if ret.isError():
    print("Error in submit:", ret.error)
    exit(1)

    print("Submitted Job")

jobId = ret.value
while True:
    ret = service.getJobProgress(jobId);
    if ret.isError():
        print("Error in progress:", ret.error)
        exit(1)

    progress = ret.value;
    if progress.status == ccmasterkernel.JobStatusJT.JobStatusJT_Completed:
        break
    elif progress.status == ccmasterkernel.JobStatusJT.JobStatusJT_Pending:
        print("Job pending")
    elif progress.status == ccmasterkernel.JobStatusJT.JobStatusJT_Running:
        print("Progress:", f"{progress.progress}%")
    elif progress.status == ccmasterkernel.JobStatusJT.JobStatusJT_Cancelled:
        print("Job cancelled")
    else:
        print("Job failed")
        exit(1)
    time.sleep(1)

print("Job done")


if CLOUD:
    ret = service.getO2DJobSettings(jobId)
    if ret.isError():
        print("Error when getting settings:", ret.error)
        exit(1)
    finalSettings = ret.value
    ret = ccmasterkernel.downloadContextScene(finalSettings.outputs.objects2D, os.path.join(output_path, "O2D_motos_バイク_cloud_test_py"), references)
    if ret.isError():
        print("Error when downloading output:", ret.error)
        exit(1)
        
    print("Successfully downloaded output")
    