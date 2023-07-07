#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: import_txt.py
# Purpose : import a custom block format
# Keywords: block creation, block import, project creation
#
# Script description:
# - creates a new CCM project,
# - reads a custom block definition from a TXT file, and creates the corresponding block.
# - export block to KML
# ******************************************************************************
import sys
import os
import csv
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
inputFilePath = 'C:/CC_SDK_DATA/data/Nice/EOsample.txt'
projectDirPath = 'C:/CC_SDK_DATA/projectPy/import-txt'

PHOTO_COL = 0
X_COL = 2
Y_COL = 3
Z_COL = 4

SENSORSIZE_MM = 5.76
FOCALLENGTH_MM = 120.
IMAGEDIMENSIONS = ccmasterkernel.ImageDimensions(800,600)
PHOTO_PREFIX = 'Photos\IMG_'
PHOTO_SUFFIX = '.tif'

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
    
    inputSRS = ccmasterkernel.SRS("WGS84")
    ECEF_SRS = ccmasterkernel.SRS("EPSG:4978")
    toECEF = ccmasterkernel.SRSTransformation(inputSRS, ECEF_SRS)
    
    # --------------------------------------------------------------------
    # create block
    # --------------------------------------------------------------------
    block=ccmasterkernel.Block(project)
    block.setPositioningLevel(ccmasterkernel.PositioningLevel.PositioningLevel_georeferenced)
    project.addBlock(block)
    
    photogroups = block.getPhotogroups()
    photogroups.addPhotogroup( ccmasterkernel.Photogroup() )
    photogroup = photogroups.getPhotogroup(photogroups.getNumPhotogroups() - 1)
    
    # --------------------------------------------------------------------
    # parse input txt file
    # --------------------------------------------------------------------
    firstPhoto = True
    
    with open(inputFilePath, 'r') as csvfile:
        rd = csv.reader(csvfile, delimiter=' ', quotechar='"', skipinitialspace=True)
        for row in rd:
            inputP = ccmasterkernel.Point3d(float(row[X_COL]), float(row[Y_COL]), float(row[Z_COL]))
            ecefP = toECEF.transform(inputP)
            
            if ecefP == None:
                print('Invalid coordinates')
                sys.exit(0)
            
            imageFilePath = os.path.join( os.path.dirname(inputFilePath), PHOTO_PREFIX + row[PHOTO_COL] + PHOTO_SUFFIX)
            photo = ccmasterkernel.Photo(imageFilePath, IMAGEDIMENSIONS)
            photo.pose.center = ecefP
            
            if firstPhoto:
                firstPhoto = False            
                photogroup.setupFromPhoto(photo)
                photogroup.sensorSize_mm = SENSORSIZE_MM
                photogroup.focalLength_mm = FOCALLENGTH_MM
            
            photogroup.addPhoto(photo)
    
    block.setChanged()
    
    block.exportToKML(os.path.join(projectDirPath, 'block.kml'))
    
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)    


if __name__ == '__main__':
    main()
