#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: processing.py
# Purpose : example of processing item creation from a job created with ServiceJobQueue.
# Keywords: processing creation, ServiceJobQueue, stand alone job
#
# Script description:
#    This script creates a project and a block from photos, 
#    then submit an object 2d detection job (O2D) on these photos, and attach the job to a processing item.
#    Finally the script browse project processing items and find back job details.
# ******************************************************************************

import sys
import os
import time
import ccmasterkernel

# Note: replace paths with your references
photosDirPath = 'C:/Users/micha/Documents/PhotogrammetryDataSets/BananaFarmOrbit30m/PFarmHouse'
projectDirPath = 'C:/CC_SDK_DATA_PROCESSING/projectPy/processing-test5'
photoObjectDetectorDirPath = 'C:/CC_SDK_DATA_PROCESSING/Data/Motos/Detector'

def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(0)

    # --------------------------------------------------------------------
    # Create project
    # --------------------------------------------------------------------
    print("# Project creation #")
    projectName = os.path.basename(projectDirPath)

    project = ccmasterkernel.Project()
    project.setName(projectName)
    project.setDescription('Automatically generated from python script')
    project.setProjectFilePath(os.path.join(projectDirPath, projectName))
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    print('Project %s successfully created.' % projectName)

    # --------------------------------------------------------------------
    # Create block from photos
    # --------------------------------------------------------------------
    block = ccmasterkernel.Block(project)
    project.addBlock(block)

    photogroups = block.getPhotogroups()
    files = os.listdir(photosDirPath)

    for file in files:
        file = os.path.join(photosDirPath, file)

        # Add photo, create a new photogroup if needed
        lastPhoto = photogroups.addPhotoInAutoMode(file)

        if lastPhoto is None:
            print('Could not add photo %s.' % file)
            continue

        # Upgrade block positioningLevel if a photo with position is found (GPS tag)
        if not lastPhoto.pose.center is None:
            block.setPositioningLevel(ccmasterkernel.PositioningLevel.PositioningLevel_georeferenced)

    # Check block
    if photogroups.getNumPhotos() == 0:
        print("Error: could not add input photos")
        exit(1)
        
    print('%s photo(s) added' % (photogroups.getNumPhotos()))
    print('')
  
    print("# Job submission #")
    
    # --------------------------------------------------------------------
    # Prepare job data
    # --------------------------------------------------------------------    
    # O2D job requires a contextScene file for input photos, create it from the block  

    productionDirPath = os.path.join(project.getProductionsDirPath(), r"Objects2D detection")
    photosContextSceneDirPath = os.path.join(productionDirPath, "photos") 
    
    err = ccmasterkernel.blockToContextScene(block, photosContextSceneDirPath, ccmasterkernel.BlockToContextSceneOptions())
    if not err.isNone():
        print(err.message)
        sys.exit(0)
        
    print("Job input data preparation completed.")
    
    # --------------------------------------------------------------------
    # Submit annotation job with ServiceJobQueue
    # -------------------------------------------------------------------- 
    
    # Define job settings
    settings = ccmasterkernel.O2DJobSettings()
    settings.inputs.photos = photosContextSceneDirPath
    settings.inputs.photoObjectDetector = photoObjectDetectorDirPath
    settings.outputs.objects2D = os.path.join(productionDirPath, "objects2D")
  
    jobQueuePath = project.getJobQueuePath();
    jobPrivateDir = os.path.join(productionDirPath, "private")
    
    print("Job details:")
    print("    JobQueue: ", jobQueuePath)
    print("    Job private dir: ", jobPrivateDir)
    print("    Job type: ", "O2D")
    print("    Inputs photos: ", settings.inputs.photos)
    print("    Inputs photoObjectDetector: ", settings.inputs.photoObjectDetector)
    print("    Outputs objects2D: ", settings.outputs.objects2D)
 
    # Submit job
    service = ccmasterkernel.ServiceJobQueue(jobQueuePath)     
    ret = service.init()
    
    if ret.isError():
        print("Error in service init:", ret.error)
        sys.exit(0)
        
    ret = service.submitJob(settings, jobPrivateDir)
    
    if ret.isError():
        print("Error in submit:", ret.error)
        sys.exit(0)
        
    jobId = ret.value
    print('Job submitted.')
    
    # --------------------------------------------------------------------
    # Attach job to a new Processing item
    # --------------------------------------------------------------------   
    processing = ccmasterkernel.Processing(project)
    processing.setName(r"Objects2D detection");
    project.addProcessing(processing)
   
    # Create a ProcessingJob instance suited for attaching ServiceJobQueue job
    processing.processingJob = ccmasterkernel.InsightProcessingJob2(processing)
    processing.processingJob.attachJob(jobQueuePath, jobId)
   
    print('Job attached to project processing.')
   
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)
        
    print('')
 
    # --------------------------------------------------------------------
    # Processings Report
    # --------------------------------------------------------------------
    # illustrate how to browse project processings and get details
    
    print("# Processings report #")
    print("%s processing(s)" % project.getNumProcessings())

    for i in range (0, project.getNumProcessings()):
        name = project.getProcessing(i).getName()
        jobId = project.getProcessing(i).processingJob.getJobId()
        jobQueuePath = project.getProcessing(i).processingJob.getJobQueuePath()
        
        # Use service to get more job details
        service = ccmasterkernel.ServiceJobQueue(jobQueuePath)       
        service.init()
        
        ret = service.getJobProgress(jobId);
        status = ret.value.status
        
        ret = service.getJobType(jobId)
        jobType = ret.value
        
        print("    [Processing - %s]" % name)
        print("    Jobqueue: ", jobQueuePath)
        print("    JobId: ", jobId)
        print("    JobType: ", jobType)
        print("    Status: ", status)
   
    print('')
    print("Done")  

if __name__ == '__main__':
    main()
