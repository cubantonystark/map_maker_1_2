#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: automaster.py
# Purpose : create a complete reconstruction from a directory of photos
# Keywords: block creation, photos, project creation, reconstruction, production, job monitoring
#
# Script description:
#    This script browses an input photo directory and manages a complete reconstruction project with default settings
#    from these photos including:
#    - AT,
#    - Reconstruction,
#    - Production in OBJ format.
# ******************************************************************************

import sys
import os
import time
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
photosDirPath = 'C:/Users/micha/Documents/PhotogrammetryDataSets/BananaFarmOrbit30m/PFarmHouse'
projectDirPath = 'C:/CC_SDK_DATA/projectPy/automaster8'


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(0)

    # --------------------------------------------------------------------
    # create project
    # --------------------------------------------------------------------
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
    print('')

    # --------------------------------------------------------------------
    # create block
    # --------------------------------------------------------------------
    block=ccmasterkernel.Block(project)
    project.addBlock(block)

    block.setName('block #1')
    block.setDescription('input block')
    photogroups = block.getPhotogroups()
    files = os.listdir(photosDirPath)

    for file in files:
        file = os.path.join(photosDirPath, file)

        # add photo, create a new photogroup if needed
        lastPhoto = photogroups.addPhotoInAutoMode(file)

        if lastPhoto is None:
            print('Could not add photo %s.' % file)
            continue

        # upgrade block positioningLevel if a photo with position is found (GPS tag)
        if not lastPhoto.pose.center is None:
            block.setPositioningLevel(ccmasterkernel.PositioningLevel.PositioningLevel_georeferenced)

    print('')

    # check block
    print('%s photo(s) added in %s photogroup(s):' % (photogroups.getNumPhotos(), photogroups.getNumPhotogroups()))

    photogroups = project.getBlock(0).getPhotogroups()

    for i_pg in range(0, photogroups.getNumPhotogroups()):
        print('photogroup #%s:' % (i_pg+1))
        if not photogroups.getPhotogroup(i_pg).hasValidFocalLengthData():
            print('Warning: invalid photogroup')
        for photo_i in photogroups.getPhotogroup(i_pg).getPhotoArray():
            print('image: %s' % photo_i.imageFilePath)

        print('')

    if not block.isReadyForAT():
        if block.reachedLicenseLimit():
            print('Error: Block size exceeds license capabilities.')
        if block.getPhotogroups().getNumPhotos() < 3:
            print('Error: Insufficient number of photos.')
        else:
            print('Error: Missing focal lengths and sensor sizes.')
        sys.exit(0)

    # --------------------------------------------------------------------
    # AT
    # --------------------------------------------------------------------
    blockAT=ccmasterkernel.Block(project)
    project.addBlock(blockAT)
    blockAT.setBlockTemplate(ccmasterkernel.BlockTemplate.Template_adjusted, block)

    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    # Set some settings
    at_settings = blockAT.getAT().getSettings()
    at_settings.keyPointsDensity = ccmasterkernel.KeyPointsDensity.KeyPointsDensity_high
    at_settings.splatsPreprocessing = ccmasterkernel.SplatsPreprocessing.SplatsPreprocessing_none
    at_settings.ColorEqualizationPreprocessing = ccmasterkernel.ColorEqualizationPreprocessing.ColorEqualizationPreprocessing_ML
    
    if not blockAT.getAT().setSettings(at_settings):
        print("Error: Failed to set settings for aerotriangulation")
        sys.exit(0)
    atSubmitError = blockAT.getAT().submitProcessing()

    if not atSubmitError.isNone():
        print('Error: Failed to submit aerotriangulation.')
        print(atSubmitError.message)
        sys.exit(0)

    print('The aerotriangulation job has been submitted and is waiting to be processed...')

    iPreviousProgress = 0
    iProgress = 0
    previousJobStatus = ccmasterkernel.JobStatus.Job_unknown
    jobStatus = ccmasterkernel.JobStatus.Job_unknown

    while 1:
        jobStatus = blockAT.getAT().getJobStatus()

        if jobStatus != previousJobStatus:
            print(ccmasterkernel.jobStatusAsString(jobStatus))

        if jobStatus == ccmasterkernel.JobStatus.Job_failed or jobStatus == ccmasterkernel.JobStatus.Job_cancelled or jobStatus == ccmasterkernel.JobStatus.Job_completed:
            break

        if iProgress != iPreviousProgress:
            print('%s%% - %s' % (iProgress,blockAT.getAT().getJobMessage()))

        iPreviousProgress = iProgress
        iProgress = blockAT.getAT().getJobProgress()
        time.sleep(1)
        blockAT.getAT().updateJobStatus()
        previousJobStatus = jobStatus

    if jobStatus != ccmasterkernel.JobStatus.Job_completed:
        print('"Error: Incomplete aerotriangulation.')

        if blockAT.getAT().getJobMessage() != '':
            print( blockAT.getAT().getJobMessage() )

    print('Aerotriangulation completed.')

    if not blockAT.canGenerateQualityReport():
        print("Error: BlockAT can't generate Quality report")
        sys.exit(0)

    if not blockAT.generateQualityReport(True):
        print("Error: failed to generate Quality report")
        sys.exit(0)

    print("AT report available at", blockAT.getQualityReportPath())

    if  not blockAT.isReadyForReconstruction():
        print('Error: Incomplete photos. Cannot create reconstruction.')
        sys.exit(0)

    print('Ready for reconstruction.')

    if blockAT.getPhotogroups().getNumPhotosWithCompletePose_byComponent(1) < blockAT.getPhotogroups().getNumPhotos():
        print('Warning: incomplete photos. %s/%s photo(s) cannot be used for reconstruction.' % ( blockAT.getPhotogroups().getNumPhotos() - blockAT.getPhotogroups().getNumPhotosWithCompletePose_byComponent(1), blockAT.getPhotogroups().getNumPhotos() ) );

    # --------------------------------------------------------------------
    # Reconstruction
    # --------------------------------------------------------------------
    reconstruction = ccmasterkernel.Reconstruction(blockAT)
    blockAT.addReconstruction(reconstruction)

    if reconstruction.getNumInternalTiles() == 0:
        print('Error: Failed to create reconstruction layout.')
        sys.exit(0)

    print('Reconstruction item created.')

    # --------------------------------------------------------------------
    # Production
    # --------------------------------------------------------------------
    production = ccmasterkernel.Production(reconstruction)
    reconstruction.addProduction(production)

    production.setDriverName('OBJ')
    production.setDestination( os.path.join(project.getProductionsDirPath(), production.getName()) )

    driverOptions = production.getDriverOptions()
    driverOptions.put_bool('TextureEnabled', True)
    driverOptions.put_int('TextureCompressionQuality', 100)
    driverOptions.writeXML( os.path.join(project.getProductionsDirPath(), "options.xml") )

    production.setDriverOptions(driverOptions)

    print('Production item created.')

    productionSubmitError = production.submitProcessing()

    if not productionSubmitError.isNone():
        print('Error: Failed to submit production.')
        print(productionSubmitError.message)
        sys.exit(0)

    print('The production job has been submitted and is waiting to be processed...')

    iPreviousProgress = 0
    iProgress = 0
    previousJobStatus = ccmasterkernel.JobStatus.Job_unknown

    while 1:
        jobStatus = production.getJobStatus()

        if jobStatus != previousJobStatus:
            print(ccmasterkernel.jobStatusAsString(jobStatus))

        if jobStatus == ccmasterkernel.JobStatus.Job_failed or jobStatus == ccmasterkernel.JobStatus.Job_cancelled or jobStatus == ccmasterkernel.JobStatus.Job_completed:
            break

        if iProgress != iPreviousProgress:
            print('%s%% - %s' % (iProgress, production.getJobMessage()))

        iPreviousProgress = iProgress
        iProgress = production.getJobProgress()
        time.sleep(1)
        production.updateJobStatus()
        previousJobStatus = jobStatus

    print('')

    if jobStatus != ccmasterkernel.JobStatus.Job_completed:
        print('"Error: Incomplete production.')

        if production.getJobMessage() != '':
            print(production.getJobMessage())

    # --------------------------------------------------------------------
    # Report
    # --------------------------------------------------------------------
    print('Production completed.')
    print('Output directory: %s' % production.getDestination())


if __name__ == '__main__':
    main()
