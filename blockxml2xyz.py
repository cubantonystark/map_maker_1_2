#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: block2xyz.py
# Purpose : import block and export poses in XYZOPK format
# Keywords: block import, custom block export, coordinate system
#
# Script description:
# - creates a new CCM project,
# - imports an input block in BlocksExchange XML format,
# - convert poses in WGS84 (if georeferenced).
# - exports poses XYZ and OPK (if rotation) in CSV format.
# ******************************************************************************

import sys
import os
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
inputBlockFilePath = 'C:/CC_SDK_DATA/Data/Paris/block.xml'
projectDirPath = 'C:/CC_SDK_DATA/projectPy/block2xyz'
outputFilePath = 'C:/CC_SDK_DATA/projectPy/block2xyz/positions.txt'
outputSRS = 'WGS84' # ignored if input block is not georeferenced


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

    # save project
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    print('Project %s successfully created.' % projectName)
    print('')

    # --------------------------------------------------------------------
    # import block
    # --------------------------------------------------------------------
    importErr = project.importBlocks(inputBlockFilePath)

    if not importErr.isNone():
        print('Failed to import block')
        print(importErr.message)
        sys.exit(0)

    # save project
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    importedBlock = project.getBlock(project.getNumBlocks() - 1)

    numPhotos = importedBlock.getPhotogroups().getNumPhotos()
    numPhotosWithPosition = 0
    numPhotosWithRotation = 0

    for i_pg in range(0, importedBlock.getPhotogroups().getNumPhotogroups()):
        for photo_i in importedBlock.getPhotogroups().getPhotogroup(i_pg).getPhotoArray():
            if photo_i.pose.center != None:
                numPhotosWithPosition = numPhotosWithPosition + 1
            if photo_i.pose.rotation != None:
                numPhotosWithRotation = numPhotosWithRotation + 1

    print("Imported block info:")
    print("- Input block: %s" % inputBlockFilePath)
    print("- Block is Georeferenced" if importedBlock.isGeoreferenced() else "- Block is Not Georeferenced")
    print("- %s photo(s)" % numPhotos)
    print("- %s photo(s) with position" % numPhotosWithPosition)
    print("- %s photo(s) with rotation" % numPhotosWithRotation)
    print('')

    if numPhotosWithPosition == 0:
        print("Error: Missing photo positions.")
        sys.exit(0)

    # --------------------------------------------------------------------
    # export blocks
    # --------------------------------------------------------------------
    output_SRS = ccmasterkernel.SRS(outputSRS)
    ECEF_SRS = ccmasterkernel.SRS("EPSG:4978")
    fromECEF = ccmasterkernel.SRSTransformation(ECEF_SRS, output_SRS)
    toECEF = ccmasterkernel.SRSTransformation(output_SRS, ECEF_SRS)

    f = open(outputFilePath, 'w')

    writeRotation = (numPhotosWithRotation == numPhotosWithPosition)

    if numPhotosWithPosition < numPhotos:
        print('Warning: incomplete positions. Photos without position will be ignored.')

    if not writeRotation and numPhotosWithRotation > 0:
        print('Warning: incomplete rotations. All rotations will be ignored.')

    if writeRotation:
        f.write("photo;x;y;z;o;p;k\n")
    else:
        f.write("photo;x;y;z\n")

    numPositionsWritten = 0

    for i_pg in range(0, importedBlock.getPhotogroups().getNumPhotogroups()):
        for photo_i in importedBlock.getPhotogroups().getPhotogroup(i_pg).getPhotoArray():
            f.write(os.path.basename(photo_i.imageFilePath))
            f.write(";")
            center = photo_i.pose.center
            rotation = photo_i.pose.rotation

            if importedBlock.isGeoreferenced():
                if center != None:
                    center = fromECEF.transform(center)
                if rotation != None:
                    R = toECEF.getRotation(center)
                    rotation.multiply(R)

            if center != None:
                f.write("%s;%s;%s" % (center.x, center.y, center.z))
            if writeRotation and rotation != None:
                opk = ccmasterkernel.matrixToOmegaPhiKappa(rotation)
                f.write(";%s;%s;%s" % (opk[0],opk[1],opk[2]))

            f.write("\n")
            numPositionsWritten = numPositionsWritten + 1

    f.close()

    print('Position file successfully created: %s' % outputFilePath)
    print('%s position(s) written' % numPositionsWritten)


if __name__ == '__main__':
    main()
