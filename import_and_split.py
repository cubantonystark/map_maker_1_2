#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: import_and_split.py
# Purpose : import and split an aerial block
# Keywords: block import, block split, block export
#
# Script description:
# - creates a new CCM project,
# - imports an aerial input block in BlocksExchange XML format, 
# - splits block,
# - exports each sub-block as a separate XML block file with ROI and list of photos.
# ******************************************************************************


import sys
import os
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
inputBlockFilePath = 'C:/CC_SDK_DATA/data/Paris/block.xml'
projectDirPath = 'C:/CC_SDK_DATA/projectPy/import-and-split'

splitMinZ = 50.
splitMaxZ = 150.
splitBaseSize = 2000.
splitMaxNumPhotos = 5000
splitSRS = ""
splitOrigin = None


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

    print("Imported block info: %s photo(s)" % importedBlock.getPhotogroups().getNumPhotos())

    # --------------------------------------------------------------------
    # split imported block
    # --------------------------------------------------------------------
    if not project.isBlockSplittable(importedBlock):
        print('Imported block is not splittable')
        sys.exit(0)

    splitParam = ccmasterkernel.SplitBlockParameters()
    splitParam.maxNumPhotos = splitMaxNumPhotos
    splitParam.sceneMinHeight = splitMinZ
    splitParam.sceneMaxHeight = splitMaxZ
    splitParam.baseSize = splitBaseSize;
    splitParam.srs = splitSRS
    splitParam.origin = splitOrigin

    splitBlockInfos = ccmasterkernel.SplitBlockInfoVec()

    print("Splitting...")
    blockSplitted = project.splitBlock(importedBlock, splitParam, splitBlockInfos)

    if not blockSplitted:
        print('Failed to split block')
        sys.exit(0)

    # --------------------------------------------------------------------
    # unload imported block
    # --------------------------------------------------------------------
    importedBlock.unload()

    # save project
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    # --------------------------------------------------------------------
    # display information on split result
    # --------------------------------------------------------------------
    print("%s sub-block(s)" % len(splitBlockInfos))

    for splitBlockInfo in splitBlockInfos:
        print("[%s]" % splitBlockInfo.block.getName())
        print("%s photo(s)" % splitBlockInfo.block.getPhotogroups().getNumPhotos())
        print("%s control point(s)" % splitBlockInfo.block.getControlPoints().getNumControlPoints())
        print("x [%s, %s] ; y [%s, %s]" % (splitBlockInfo.xMin,splitBlockInfo.xMax,splitBlockInfo.yMin,splitBlockInfo.yMax))

    # --------------------------------------------------------------------
    # export blocks
    # --------------------------------------------------------------------
    subBlocksDirPath = os.path.join(projectDirPath, 'Sub-blocks')
    if not os.path.exists(subBlocksDirPath): os.makedirs(subBlocksDirPath)

    for splitBlockInfo in splitBlockInfos:
        subBlockDirPath = os.path.join(subBlocksDirPath, splitBlockInfo.block.getName())
        if not os.path.exists(subBlockDirPath): os.makedirs(subBlockDirPath)

        # export sub-block to BlocksExchange XML file
        exportOptions = ccmasterkernel.BlockExportOptions()
        subBlockExportedErr = splitBlockInfo.block.exportToBlocksExchangeXML(os.path.join(subBlockDirPath,'block.xml'), exportOptions)

        if not subBlockExportedErr.isNone():
            print('Failed to export sub-block %s' % splitBlockInfo.block.getName())

        # export sub-block ROI in TXT file
        f = open(os.path.join(subBlockDirPath,'ROI.txt'), 'w')
        f.write("X min: %s\n" % splitBlockInfo.xMin)
        f.write("X max: %s\n" % splitBlockInfo.xMax)
        f.write("Y min: %s\n" % splitBlockInfo.yMin)
        f.write("Y max: %s\n" % splitBlockInfo.yMax)
        f.close()

        # export sub-block photo list in TXT file
        f = open(os.path.join(subBlockDirPath,'photos.txt'), 'w')

        for i_pg in range(0, splitBlockInfo.block.getPhotogroups().getNumPhotogroups()):
            for photo_i in splitBlockInfo.block.getPhotogroups().getPhotogroup(i_pg).getPhotoArray():
                f.write(photo_i.imageFilePath)
                f.write('\n')

        f.close()


if __name__ == '__main__':
    main()

