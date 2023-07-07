#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2018 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: app-info.py
# Purpose : get information about an application
# Keywords: production driver, production driver options, license
#
# Script description:
# This script shows how to extract general information about the python module: 
#   license and capabilities, supported production formats, options, etc.
# ******************************************************************************

import sys
import ccmasterkernel


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('Edition %s' % ccmasterkernel.edition())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(0)

    # --------------------------------------------------------------------
    # Display list of supported production formats
    # --------------------------------------------------------------------
    print('List of supported production formats:')
    print('')

    def driverTypeAsString(type):
        if type == ccmasterkernel.ProductionDriverType.ProductionDriver_pointCloud:
            return 'PointCloud'
        elif type == ccmasterkernel.ProductionDriverType.ProductionDriver_mesh:
            return 'Mesh'
        elif type == ccmasterkernel.ProductionDriverType.ProductionDriver_orthoDSM:
            return 'OrthoDSM'
        elif type == ccmasterkernel.ProductionDriverType.ProductionDriver_insights:
            return 'Insights'
        else:
            return 'Unknown'

    numDrivers = ccmasterkernel.ProductionDriverManager.getNumDrivers()

    for i in range (0, numDrivers):
        driver = ccmasterkernel.ProductionDriverManager.getDriver(i)
        print('[%s] (%s)' % (driver.getShortName(),driverTypeAsString(driver.getType())))
        print('   ', driver.getLongName())
        print('   ', driver.getDescription())
        print()

    print()

    # --------------------------------------------------------------------
    # Get supported options on OBJ production format (example)
    # --------------------------------------------------------------------
    ptOptionsDesc = ccmasterkernel.PropertyTree()
    objDriver = ccmasterkernel.ProductionDriverManager.getDriverByName('OBJ')

    print('Supported options on production format OBJ (example):')
    objDriver.getOptionsMetaDescription(ptOptionsDesc)
    print(ptOptionsDesc.dump())
    print()


if __name__ == '__main__':
    main()
