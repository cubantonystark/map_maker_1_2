#!/usr/bin/env python
# ******************************************************************************
# Copyright (c) 2020 Bentley Systems, Incorporated. All rights reserved.
# ******************************************************************************
# ContextCapture MasterKernel Python SDK - example script
#
# Script: jobqueue.py
# Purpose : Monitor a job queue
# Keywords: job tasks monitoring
#
# Script description:
#    This script targets a directory (the job queue path) and prints some info about ongoing jobs.
# ******************************************************************************
import sys
import os
import time
import ccmasterkernel

# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
jobQueuePath = 'C:\\JobQueueFolder'


def main():
    print('MasterKernel version %s' % ccmasterkernel.version())
    print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(1)

    monitor = ccmasterkernel.JobTaskMonitor(jobQueuePath)

    # Get pending jobs submitted in the last 24 hours
    job_names = monitor.getJobs(24, 1, 0)
    print("{} jobs retrieved ".format(len(job_names)))
    # Upgrade Normal Priorities to High
    upgraded_jobs = []
    for job_name in job_names:
        job = monitor.getJobDetails(job_name)
        if not job.valid:
            raise Exception('Invalid job {}'.format(job_name))
        print("{} priority is set to {}".format(job_name, job.priority))
        if job.priority == ccmasterkernel.JobPriority.JobPriority_Normal:
            ok = monitor.setJobPriority(job_name, ccmasterkernel.JobPriority.JobPriority_High)
            if ok:
                upgraded_jobs.append(job_name)
            else:
                print("Can't change priority to High for job {}".format(job_name))

    # Check them
    for job_name in upgraded_jobs:
        job = monitor.getJobDetails(job_name)
        if not job.valid:
            raise Exception('Invalid job details {}'.format(job_name))
        print("{} priority set to {}".format(job_name, job.priority))
        assert(job.priority == ccmasterkernel.JobPriority.JobPriority_High)


if __name__ == '__main__':
    main()
