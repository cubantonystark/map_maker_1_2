#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: project_get_version.py
# Purpose : Retrieve the project version/edition
# Keywords: job tasks monitoring
#
# Script description:
#    This script targets a ccm file and retrieves its version/edition
# ******************************************************************************

import ccmasterkernel

# Note: replace paths with your references
ccmPath = 'E:\\Projects\\18_Project\\18_Project.ccm'

def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')
    
    version = ccmasterkernel.Project.getProjectVersion(ccmPath)
    edition = ccmasterkernel.Project.getProjectEdition(ccmPath)
    print("Version", version)
    print("Edition", edition)

if __name__ == '__main__':
    main()