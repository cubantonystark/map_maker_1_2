#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: import_and_extract.py
# Purpose : import an aerial block and export extracted block
# Keywords: block import, block export, block extract, project creation
#
# Script description:
# - creates a new CCM project,
# - imports an aerial input block in BlocksExchange XML format, 
# - creates a block extract according to an input KML file, 
# - exports the extracted block in BlocksExchange XML format, and writes the list of used photos in a simple TXT file.
# ******************************************************************************

import sys
import os
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
inputBlockFilePath = 'C:/CC_SDK_DATA/data/Paris/block.xml'
roiKmlFilePath = 'C:/CC_SDK_DATA/data/Paris/ROI.kml'
projectDirPath = 'C:/CC_SDK_DATA/projectPy/import-and-extract'

extractMinZ = 50.
extractMaxZ = 150.


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    # --------------------------------------------------------------------
    # create project
    # --------------------------------------------------------------------
    projectName = os.path.basename(projectDirPath)

    project=ccmasterkernel.Project()
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

    # --------------------------------------------------------------------
    # extract imported block
    # --------------------------------------------------------------------
    if not project.isBlockExtractable(importedBlock):
        print('Imported block is not extractable')
        sys.exit(0)

    extractROI = ccmasterkernel.ROI()
    kmlLoaded = extractROI.importFromKML(roiKmlFilePath, "EPSG:3857")

    if not kmlLoaded:
        print('Failed to load kml file')
        sys.exit(0)

    extractROI.setMinMaxZ(extractMinZ, extractMaxZ)
    blockExtracted = project.extractBlock(importedBlock, "EPSG:3857", extractROI)

    if not blockExtracted:
        print('Failed to extract block')
        sys.exit(0)

    extractedBlock = project.getBlock(project.getNumBlocks() - 1)

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
    # export extracted block
    # --------------------------------------------------------------------

    # export BlocksExchange XML file
    exportOptions = ccmasterkernel.BlockExportOptions()

    blockExportedErr = extractedBlock.exportToBlocksExchangeXML(os.path.join(projectDirPath,'block-extract.xml'), exportOptions)

    if not blockExportedErr.isNone():
        print('Failed to export block extract')
        sys.exit(0)

    # export photo list in TXT file
    f = open(os.path.join(projectDirPath,'block-photos.txt'), 'w')

    for i_pg in range(0, extractedBlock.getPhotogroups().getNumPhotogroups()):
        for photo_i in extractedBlock.getPhotogroups().getPhotogroup(i_pg).getPhotoArray():
            f.write(photo_i.imageFilePath)
            f.write('\n')

    f.close()


if __name__ == '__main__':
    main()
