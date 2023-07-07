#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: dump_project.py
# Purpose : dump data from an existing ContextCapture project
# Keywords: project reading, project data acess
#
# Script description: This script loads a sample project and displays project contents.
# ******************************************************************************

import sys
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
projectFilePath = 'C:/CC_SDK_DATA/Data/Paris/Project/Paris.ccm'


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    # --------------------------------------------------------------------
    # load project
    # --------------------------------------------------------------------
    project = ccmasterkernel.Project()
    err = project.readFromFile(projectFilePath)
    if not err.isNone():
        print('Failed to load project. ' + err.message)
        sys.exit(0)

    print('Project %s successfully loaded.' % project.getName())
    print('')

    # --------------------------------------------------------------------
    # display project tree
    # --------------------------------------------------------------------
    for iBlock in range(0, project.getNumBlocks()):
        block = project.getBlock(iBlock)
        print(' -[%s]' % block.getName())
        for iReconstruction in range(0, block.getNumReconstructions()):
            reconstruction = block.getReconstruction(iReconstruction)
            print('     -[%s]' % reconstruction.getName())
            for iProduction in range(0, reconstruction.getNumProductions()):
                production = reconstruction.getProduction(iProduction)
                print('         -[%s]' % production.getName())


    print('')

    # --------------------------------------------------------------------
    # display block details
    # --------------------------------------------------------------------
    for iBlock in range(0, project.getNumBlocks()):
        block = project.getBlock(iBlock)

        print('--------------------------------------')
        print('[%s]:' % block.getName())

        # AT
        AT = block.getAT()
        if AT != None:
            print('-AT:')
            print('    positioning mode: %s' % AT.getPositioningModeAsString(AT.getPositioningMode()))
            ATSettings = AT.getSettings()
            print('    pair selection mode: %s' % ATSettings.getPairSelectionModeAsString(ATSettings.pairSelectionMode))
            print('    keyPoints density: %s' % ATSettings.getKeyPointsDensityAsString(ATSettings.keyPointsDensity))
            print('    component construction mode: %s' % ATSettings.getComponentConstructionModeAsString(ATSettings.componentConstructionMode))
            print('    rotation policy: %s' % ATSettings.rotationPolicy.toString())
            print('    center policy: %s' % ATSettings.centerPolicy.toString())
            print('    focal policy: %s' % ATSettings.focalPolicy.toString())
            print('    principal policy: %s' % ATSettings.principalPolicy.toString())
            print('    radial policy: %s' % ATSettings.radialPolicy.toString())
            print('    tangential policy: %s' % ATSettings.tangentialPolicy.toString())
            print('    tiePoints policy: %s' % ATSettings.tiePointsPolicy.toString())
            print('')

        # photogroups/photos
        photogroups = block.getPhotogroups()
        print('%s photo(s) in %s photogroup(s):' % (photogroups.getNumPhotos(), photogroups.getNumPhotogroups()))

        for i_pg in range(0, photogroups.getNumPhotogroups()):
            print('photogroup #%s:' % (i_pg+1))
            if not photogroups.getPhotogroup(i_pg).hasValidFocalLengthData():
                print('Warning: invalid photogroup')

            print('id: %s' % photogroups.getPhotogroup(i_pg).id)
            print('name: %s' % photogroups.getPhotogroup(i_pg).name)
            print('description: %s' % photogroups.getPhotogroup(i_pg).description)
            print('sensorSizeDB_mm: %s' % photogroups.getPhotogroup(i_pg).sensorSizeDB_mm)
            print('focalLengthDB_mm: %s' % photogroups.getPhotogroup(i_pg).focalLengthDB_mm)

            if photogroups.getPhotogroup(i_pg).imageDimensions != None:
                print('imageDimensions: %sx%s' % (photogroups.getPhotogroup(i_pg).imageDimensions.width,photogroups.getPhotogroup(i_pg).imageDimensions.height))
            else:
                print('imageDimensions: None')

            print('sensorSize_mm: %s' % photogroups.getPhotogroup(i_pg).sensorSize_mm)
            print('focalLength_mm: %s' % photogroups.getPhotogroup(i_pg).focalLength_mm)

            if photogroups.getPhotogroup(i_pg).distortion != None:
                print('distortion: k1 %s, k2 %s, k3 %s, p1 %s, p2 %s' % (photogroups.getPhotogroup(i_pg).distortion.k1,photogroups.getPhotogroup(i_pg).distortion.k2,photogroups.getPhotogroup(i_pg).distortion.k3,photogroups.getPhotogroup(i_pg).distortion.p1,photogroups.getPhotogroup(i_pg).distortion.p2))
            else:
                print('distortion: None')

            if photogroups.getPhotogroup(i_pg).principalPoint != None:
                print('principalPoint: %s,%s' % (photogroups.getPhotogroup(i_pg).principalPoint.x,photogroups.getPhotogroup(i_pg).principalPoint.y))
            else:
                print('principalPoint: None')

            print(''),

            for photo_i in photogroups.getPhotogroup(i_pg).getPhotoArray():
                print('image: %s' % photo_i.imageFilePath)
                print('mask: %s' % photo_i.maskFilePath)
                print('id: %s' % photo_i.id)
                print('component: %s' % photo_i.component)

                if photo_i.pose.center:
                    print('pose center: %s,%s,%s' % (photo_i.pose.center.x,photo_i.pose.center.y,photo_i.pose.center.z))
                else:
                    print('pose center: None')

                if photo_i.pose.rotation:
                    print('pose rotation: defined')
                else:
                    print('pose rotation: None')

                if photo_i.imageDimensions != None:
                    print('imageDimensions: %sx%s' % (photo_i.imageDimensions.width,photo_i.imageDimensions.height))
                else:
                    print('imageDimensions: None')

                print('')
                print('exif data:')
                if photo_i.exifData.imageDimensions != None:
                    print('-imageDimensions: %sx%s' % (photo_i.exifData.imageDimensions.width,photo_i.exifData.imageDimensions.height))
                else:
                    print('-imageDimensions: None')

                if photo_i.exifData.pixelDimensions != None:
                    print('-pixelDimensions: %sx%s' % (photo_i.exifData.pixelDimensions.width,photo_i.exifData.pixelDimensions.height))
                else:
                    print('-pixelDimensions: None')

                print('-GPS: lat %s, lon %s, alt %s' % (photo_i.exifData.GPSLatitude, photo_i.exifData.GPSLongitude, photo_i.exifData.GPSAltitude))
                print('-focal length: %s' %photo_i.exifData.focalLength)
                print('-focal length 35mm: %s' %photo_i.exifData.focalLength35mm)
                print('-make: %s' % photo_i.exifData.make)
                print('-model: %s' % photo_i.exifData.model)
                print('-dateTimeOriginal: %s' % photo_i.exifData.dateTimeOriginal)
                print('')

            print('')

        if not block.isReadyForAT():
            if block.reachedLicenseLimit():
                print('Not ready for AT: Block size exceeds license capabilities.')
            if block.getPhotogroups().getNumPhotos() < 3:
                print('Not ready for AT: Insufficient number of photos.')
            else:
                print('Not ready for AT: Missing focal lengths and sensor sizes.')

        print('Reconstructions:')
        for iReconstruction in range(0, block.getNumReconstructions()):
            reconstruction = block.getReconstruction(iReconstruction)

            print('-[%s]:' % reconstruction.getName())

            # --------------------------------------------------------------------
            # display reconstruction details
            # --------------------------------------------------------------------
            print('    SRS:', reconstruction.getSRS())

            bbox = reconstruction.getROI().getBoundingBox()
            print('    ROI (extent) x:[%s,%s], y:[%s,%s]' % (bbox.xMin, bbox.xMax, bbox.yMin, bbox.yMax))
            print()

            print('    Tiling:')
            tiling = reconstruction.getTiling()
            print('    -Mode:', tiling.tilingMode)
            print('    -TileSize:', tiling.tileSize)

            if tiling.customOrigin:
                print('    -CustomOrigin: (%s,%s,%s)' % (tiling.customOrigin.x, tiling.customOrigin.y, tiling.customOrigin.z))

            print()

            print('    Processing settings:')
            settings = reconstruction.getSettings()
            print('    -Geometry precision mode:', settings.geometryPrecisionMode)
            print('    -Hole filling mode:', settings.holeFillingMode)
            print('    -Pair selection mode:', settings.pairSelectionMode)


if __name__ == '__main__':
    main()
