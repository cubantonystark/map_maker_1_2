#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: compute_orthophoto.py
# Purpose : Create an orthophoto from a calibrated block
# Keywords: ortho, orthophoto, dsm
#
# Script description:
# - creates a new CCM project,
# - imports an input block with tiepoints in BlocksExchange XML format, 
# - Create new orthophoto,
# - Submit production.
# ******************************************************************************

import sys
import os
import time
import ccmasterkernel

projectDirPath = 'C:/CC_SDK_DATA/projectPy/Orthophoto_25d'
blockXmlPath = 'C:/CC_SDK_DATA/Data/Drone/Drone.xmlz'  # Has to contain TiePoints

def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(0)

    # --------------------------------------------------------------------
    # Create project
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
    # Import Block
    # --------------------------------------------------------------------
    import_err = project.importBlocks(blockXmlPath)
    if not import_err.isNone():
        print(import_err.message)
        sys.exit(0)
        
    print('Block %s successfully created.' % blockXmlPath)
    print('')
    # --------------------------------------------------------------------
    # Create Orthophoto/DSM
    # --------------------------------------------------------------------
    block = project.getBlock(0)
    reconstruction = ccmasterkernel.Reconstruction(block)
    reconstruction.setName('Orthophoto/DSM')
    r_settings = ccmasterkernel.ReconstructionSettings()
    
    r_settings.type = ccmasterkernel.ReconstructionType.Type_25d
    r_settings.geometryPrecisionMode = ccmasterkernel.GeometryPrecisionMode.GeometryPrecision_medium
    reconstruction.setSettings(r_settings)
    block.addReconstruction(reconstruction)
    
    # --------------------------------------------------------------------
    # Create Production
    # --------------------------------------------------------------------
    production = ccmasterkernel.Production(reconstruction)
    production.setDriverName("Orthophoto/DSM")
    production.setDestination('C:/CC_SDK_DATA/Projects/Orthophoto_25d/Productions/Production_1')
    
    driverOptions = production.getDriverOptions() 
    # Set SRS
    driverOptions.put_string("SRS", "EPSG:4979")
    production.setDriverOptions(driverOptions)
    # Set sampling distance to default value
    defaultSamplingDistanceOption = production.getDefaultDriverOption("SamplingDistance")
    samplingDistance = defaultSamplingDistanceOption.get_double("", 0.1)
    driverOptions.put_double("SamplingDistance", samplingDistance)
    production.setDriverOptions(driverOptions)    
    # Set production extent to default value
    defaultExtentOption = production.getDefaultDriverOption("Extent")
    extent = defaultExtentOption.get_multiPolygon2d("", ccmasterkernel.MultiPolygon2d())
    driverOptions.put_multiPolygon2d("Extent", extent)
    production.setDriverOptions(driverOptions)

    reconstruction.addProduction(production)
    print('Orthophoto added')
    project.writeToFile()
    
    # --------------------------------------------------------------------
    # Submit Processing
    # --------------------------------------------------------------------
    error_process = production.submitProcessing()
    if not error_process.isNone():
        print(error_process.message)
    
    print('Orthophoto submitted')
    block.setChanged()
    project.writeToFile()
    
if __name__ == '__main__':
    main()
