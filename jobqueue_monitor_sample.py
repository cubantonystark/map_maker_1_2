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
import itwincapturemodeler


# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
jobQueuePath = "C:/Users/micha/Documents/Bentley/iTwin Capture Modeler/Jobs"

ccmasterkernel = itwincapturemodeler
def main():
    # print('MasterKernel version %s' % ccmasterkernel.version())
    # print('')

    if not ccmasterkernel.isLicenseValid():
        print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
        sys.exit(1)

    monitor = ccmasterkernel.JobTaskMonitor(jobQueuePath)
    # print("running loop")
    jobs = monitor.getJobs(24, 1, 0)
    jobs_details = []
    for j in jobs:  # extract all jobs
        details = monitor.getJobDetails(j)
        if not details.valid:
            # print('Invalid job details {} ({})'.format(j, details.valid_error_as_str()))
            continue
        jobs_details.append(details)

    jobs_details.sort(key=lambda x: x.status)
    jobs = []
    for j in jobs_details:
        # print('job {} ({}), status {}, submitTime {}, placeInTheQueue {}'.format(j.name, j.description, j.status,
        #                                                                          j.submit_time,
        #                                                                          j.place))
        if j.percent != 100:
            if "Failed" not in str(j.status):
                job = {'job': j.name,
                       'description': j.description,
                       'percentage': j.percent,
                       'status': j.status,
                       'start_time': j.start_time,
                       'end_time': j.end_time,
                       'place': j.place,
                       }
                jobs.append(job)
    ''' Possible arguments :
        Job_Detail : monitor.getJobDetails(j)
            j.place :               The place in the queue
            j.percent :             Current percent
            j.status :              Status of the job   
            j.name :                Name of the job
            j.description :         Description of job
            j.submit_host :         Who submitted it
            j.project_path :        Project path of the job
            j.submit_time :         Submit time of the job
            j.start_time :          Start time of the job
            j.end_time :            End time of the job
            j.processing_hosts :    All engines processing job's tasks

        Job_Diagnostics : monitor.getJobDiagnostic(j)
            j.pending :     Number of pending tasks in the job
            j.ready :       Number of ready tasks in the job
            j.running :     Number of running tasks in the job
            j.completed :   Number of completed tasks in the job
            j.failed :      Number of failed tasks in the job
            j.cancelled :   Number of cancelled tasks in the job
    '''
    # time.sleep(5)

    return jobs
# if __name__ == '__main__':
#     main()

