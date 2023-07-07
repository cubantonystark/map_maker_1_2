#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: reconstruction_settings.py
# Purpose : create a new reconstruction in an existing ContextCapture project
# Keywords: project reading, reconstruction settings
#
# Script description: This script loads a sample project and creates a new reconstruction with custom settings.
# ******************************************************************************

import sys
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
projectFilePath = 'C:/CC_SDK_DATA/Data/Paris/Project/Paris.ccm'
roiFilePath = 'C:/CC_SDK_DATA/Data/Paris/ROI.kml'
blockIndex = 1
srs = 'EPSG:2154'


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(0)

    # --------------------------------------------------------------------
    # load project
    # --------------------------------------------------------------------
    project = ccmasterkernel.Project()
    err = project.readFromFile(projectFilePath)
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    print('Project %s successfully loaded.' % project.getName())
    print('')

    # --------------------------------------------------------------------
    # check block
    # --------------------------------------------------------------------
    if blockIndex > project.getNumBlocks():
        print('Error: block index out of range')
        sys.exit(0)

    block = project.getBlock(blockIndex)

    if not block.isGeoreferenced():
        print('Error: block not georeferenced')
        sys.exit(0)

    if not block.isReadyForReconstruction():
        print('Error: block not ready for reconstruction')
        sys.exit(0)

    # --------------------------------------------------------------------
    # create reconstruction
    # --------------------------------------------------------------------
    reconstruction = ccmasterkernel.Reconstruction(block)
    block.addReconstruction(reconstruction)

    reconstruction.setDescription('Automatically generated from python script')

    # ---
    # SRS
    # ---
    if not reconstruction.setSRS(srs):
        print('Invalid reconstruction SRS')
        sys.exit(0)

    # ---
    # ROI
    # ---
    kmlROI = ccmasterkernel.ROI()
    kmlLoaded = kmlROI.importFromKML(roiFilePath, srs)

    if not kmlLoaded:
        print('Failed to load ROI kml file')
        sys.exit(0)

    # keep default zMin/zMax
    defaultBBox = reconstruction.getDefaultROI().getBoundingBox()
    kmlROI.setMinMaxZ(defaultBBox.zMin, defaultBBox.zMax)

    reconstruction.setROI(kmlROI)

    # ------
    # Tiling
    # ------
    tiling = reconstruction.getTiling()
    tiling.tilingMode = ccmasterkernel.TilingMode.TilingMode_regularPlanarGrid
    tiling.tileSize = 200
    tiling.customOrigin = ccmasterkernel.Point3d(651500, 6861500, 0)

    reconstruction.setTiling(tiling)

    # -------------------
    # Processing settings
    # -------------------
    settings = reconstruction.getSettings()
    settings.geometryPrecisionMode = ccmasterkernel.GeometryPrecisionMode.GeometryPrecision_extra
    settings.holeFillingMode = ccmasterkernel.HoleFillingMode.HoleFilling_allHoles
    settings.pairSelectionMode = ccmasterkernel.ReconstructionPairSelectionMode.ReconstructionPairSelection_forStructuredAerialDataset

    reconstruction.setSettings(settings)

    block.setChanged()

    # --------------------------------------------------------------------
    # Save project
    # --------------------------------------------------------------------
    err = project.writeToFile()
    if not err.isNone():
        print(err.message)
        sys.exit(0)

    # --------------------------------------------------------------------
    # Display actual reconstruction settings
    # --------------------------------------------------------------------
    print()
    print('Reconstruction settings:')

    print('SRS:', reconstruction.getSRS())

    bbox = reconstruction.getROI().getBoundingBox()
    print('ROI (extent) x:[%s,%s], y:[%s,%s]' % (bbox.xMin, bbox.xMax, bbox.yMin, bbox.yMax))
    print()

    print('Tiling:')
    tiling = reconstruction.getTiling()
    print('-Mode:', tiling.tilingMode)
    print('-TileSize:', tiling.tileSize)

    if tiling.customOrigin:
        print('-CustomOrigin: (%s,%s,%s)' % (tiling.customOrigin.x, tiling.customOrigin.y, tiling.customOrigin.z))

    print()

    print('Processing settings:')
    settings = reconstruction.getSettings()
    print('-Geometry precision mode:', settings.geometryPrecisionMode)
    print('-Hole filling mode:', settings.holeFillingMode)
    print('-Pair selection mode:', settings.pairSelectionMode)

    print()
    print('Number of tiles:', reconstruction.getNumInternalTiles())


if __name__ == '__main__':
    main()
