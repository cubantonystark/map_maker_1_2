#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2021 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: generateLOD_standalone.py
# Purpose : generate a 3D mesh with LOD from reference tiles of different reconstructions or projects
# Keywords: LOD, tiles, mesh
#
# Script description:
# - creates a new job for LOD generation from a CCGenerateLODInput XML file,
# - sets driver options for the output 3D model,
# - submits the job,
# - monitors the job.
# ******************************************************************************

import ccmasterkernel
import time

input_xml = "C:/Projects/Standalone/input.xml"
output_dir = "C:/Projects/Standalone/output"

def monitor_job(job_name, job_queue):
    print('Monitoring job ' + job_name + ' from job queue ' + job_queue)
    monitor = ccmasterkernel.JobTaskMonitor(job_queue)
    iPreviousProgress = 0
    previousJobStatus = ccmasterkernel.JobStatusJT.JobStatusJT_None
    while 1:
        jobDet = monitor.getJobDetails(job_name)
        jobStatus = jobDet.status
        if jobStatus != previousJobStatus:
            print(job_name + " is now", end=' ', flush=True)
            print(jobStatus, flush=True)
            previousJobStatus = jobStatus
        if jobStatus == ccmasterkernel.JobStatusJT.JobStatusJT_Failed or jobStatus == ccmasterkernel.JobStatusJT.JobStatusJT_Cancelled or jobStatus == ccmasterkernel.JobStatusJT.JobStatusJT_Completed:
            break
        iProgress = int(jobDet.percent)
        if iProgress != iPreviousProgress:
            print('%d%%' % (iProgress), end=' ', flush=True)
            iPreviousProgress = iProgress
        time.sleep(3)
    print()

job = ccmasterkernel.GenerateLODStandaloneJob(input_xml, '3SM', output_dir)
driverOps = job.getDriverOptions()
driverOps.put_string('SRS', 'EPSG:32631')
job.setDriverOptions(driverOps)
err = job.submit()
if not err.isNone():
    print("We have an issue: " + err.message)
    exit(1)
monitor_job(job.getJobName(), job.getJobQueue())
exit(0)
