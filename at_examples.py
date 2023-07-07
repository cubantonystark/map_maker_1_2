#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2022 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# These are code snippets for some possible AT scenarios
# ******************************************************************************

import ccmasterkernel
import os
import sys


def add_control_points_and_adjust_at(project, block):
    """
    This snippet adds 3 control points to the block, then set the AT to be adjusted on these control points
    """
    srs_manager = project.getProjectSRSManager()
    srs_cp_id = srs_manager.getOrCreateProjectSRSId("EPSG:3945+5720",
                                                    "RGF93 / CC45 (EPSG:3945) + NGF-IGN69 height (EPSG:5720)")

    control_points = block.getControlPoints()

    # Control point #1
    cp = ccmasterkernel.ControlPoint()
    cp.name = "CP #1"
    cp.checkPoint = False
    cp.category = ccmasterkernel.ControlPointCategory.ControlPoint_full
    cp.position = ccmasterkernel.Point3d(1830948.7, 4230789.177, 404.455)
    cp.horizontalAccuracy = 0.01
    cp.verticalAccuracy = 0.001
    cp.srsId = srs_cp_id

    m1 = ccmasterkernel.Measurement()
    m1.photoId = 0
    m1.imagePosition = ccmasterkernel.Point2d(1705.41, 2477.77)
    m2 = ccmasterkernel.Measurement()
    m2.photoId = 1
    m2.imagePosition = ccmasterkernel.Point2d(1230.20, 1689.16)
    m3 = ccmasterkernel.Measurement()
    m3.photoId = 2
    m3.imagePosition = ccmasterkernel.Point2d(1793.09, 1389.48)
    cp.addMeasurement(m1)
    cp.addMeasurement(m2)
    cp.addMeasurement(m3)
    control_points.addControlPoint(cp)

    # Control point #2
    cp = ccmasterkernel.ControlPoint()
    cp.name = "CP #2"
    cp.checkPoint = False
    cp.category = ccmasterkernel.ControlPointCategory.ControlPoint_full
    cp.position = ccmasterkernel.Point3d(1830947.882, 4230833.182, 402.28)
    cp.horizontalAccuracy = 0.01
    cp.verticalAccuracy = 0.001
    cp.srsId = srs_cp_id

    m1 = ccmasterkernel.Measurement()
    m1.photoId = 0
    m1.imagePosition = ccmasterkernel.Point2d(2307.24, 750.27)
    m2 = ccmasterkernel.Measurement()
    m2.photoId = 1
    m2.imagePosition = ccmasterkernel.Point2d(3151.42, 1012.82)
    m3 = ccmasterkernel.Measurement()
    m3.photoId = 2
    m3.imagePosition = ccmasterkernel.Point2d(3708.67, 1265.55)
    cp.addMeasurement(m1)
    cp.addMeasurement(m2)
    cp.addMeasurement(m3)
    control_points.addControlPoint(cp)

    # Control point #2
    cp = ccmasterkernel.ControlPoint()
    cp.name = "CP #3"
    cp.checkPoint = False
    cp.category = ccmasterkernel.ControlPointCategory.ControlPoint_full
    cp.position = ccmasterkernel.Point3d(1830971.335, 4230804.956, 399.554)
    cp.horizontalAccuracy = 0.01
    cp.verticalAccuracy = 0.001
    cp.srsId = srs_cp_id

    m1 = ccmasterkernel.Measurement()
    m1.photoId = 0
    m1.imagePosition = ccmasterkernel.Point2d(3267.83, 1943.10)
    m2 = ccmasterkernel.Measurement()
    m2.photoId = 1
    m2.imagePosition = ccmasterkernel.Point2d(2441.11, 2336.43)
    m3 = ccmasterkernel.Measurement()
    m3.photoId = 2
    m3.imagePosition = ccmasterkernel.Point2d(2473.09, 2237.97)
    cp.addMeasurement(m1)
    cp.addMeasurement(m2)
    cp.addMeasurement(m3)
    control_points.addControlPoint(cp)

    project.writeToFile()

    # Now that control points are added, create AT
    block_at = ccmasterkernel.Block(project)
    project.addBlock(block_at)
    block_at.setBlockTemplate(ccmasterkernel.BlockTemplate.Template_adjusted, block)

    # Set settings for adjustments
    at_settings = block_at.getAT().getSettings()
    at_settings.adjustmentConstraints = ccmasterkernel.AdjustmentAndPositioning.Positioning_ControlPoints
    block_at.getAT().setSettings(at_settings)

    block_at.getAT().submitProcessing()
    project.writeToFile()
