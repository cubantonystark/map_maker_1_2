
# Script: built off automaster.py

import shutil
import subprocess
import sys
import os
import time
import array as arr

import itwincapturemodeler
import random

#import pymeshlab
import requests
from numpy import array

import MM_logger
import xml.etree.ElementTree as ET
from MM_objects import MapmakerProject

ccmasterkernel = itwincapturemodeler
# Note: replace paths with your references, or install SDK sample data in C:/CC_SDK_DATA
photosDirPath = os.getcwd()+'/ARTAK_MM/DATA/Raw_Images/UNZIPPED'
projectDir = os.getcwd()+'/ARTAK_MM/POST/Photogrammetry/'

# base_url = "https://esp.eastus2.cloudapp.azure.com/"
# dit_host = "https://esp.eastus2.cloudapp.azure.com/dit/v1/"



class processing_photogrammetry():

    def __init__(self, file_name, logger, _cesium=False, mm_project=MapmakerProject()):

        self.projecDirPath = projectDir + file_name + str(random.randint(1,1000))
        self.photosDirPath = os.path.join(os.getcwd()+'/ARTAK_MM/DATA/Raw_Images/UNZIPPED/', file_name)
        self.logger = logger
        self.logger.info("Initialized PG")
        self.cesium = _cesium
        self.filename = file_name
        self.mm_project = mm_project
        self.artak_server = self.mm_project.artak_server
        self.logger.info (mm_project.as_dict())

    def _test_login(self, url):
        # Add Eolian API key "x-api-key" and "x-login-from" to headers to be able to get a session key
        # Need to have an empty files dict to make the request encode as multipart.form-data rather than
        # application/x-www-form-urlencoded.
        r = requests.post(
            url=url + "login",
            headers={
                "x-api-key": "isxZRh&agnaYH^jtMR%NGke5VYJ3kGW2kiWgmfGLVTWqABdHMVY5Q5q!nnzk",
                "x-login-from": "device"
            },
            data={"user_name": "test_username"},
            files={},
            # verify=verify_ssl
        )
        response = r.json()

        # logger.info(f"Login Response: {response}")
        self.logger.info(response)
        if response["status"] == 'Success':
            session_token = str(response["data"])
        self.logger.info(session_token)
        return session_token

    def upload_to_artak_server(self, file_dict: dict, data: dict, url):
        upload_url = url + "dit/v1/"
        session_token = self._test_login(url)
        self.logger.info("login url = " + url)
        self.logger.info("upload url = " + upload_url)
        r = requests.post(
            upload_url + "upload",
            data=data,
            headers={"x-api-key": session_token},
            files=file_dict,
        )
        return r

    def upload(self, the_file, url="https://esp.eastus2.cloudapp.azure.com/"):
        self.logger.info("Sending the file =" + the_file)
        file_zip = open(the_file, "rb")
        payload = {"file": file_zip}
        params = {"type": "maps"}
        self.logger.info("url : " + url)
        response = self.upload_to_artak_server(file_dict=payload, data=params, url=url)
        self.logger.info(response)
        return response

    #  logger.info(f"upload A77_EO.zip Response: {response}")

    def do_photogrammetry(self):
        self.logger.info("Starting Photogrammetry Job. Project path directory = " + self.projecDirPath)
        self.logger.info("Starting Photogrammetry Job. Source photos directory = " + self.photosDirPath)
        self.mm_project.time_processing_start = time.time()
        self.logger.info('MasterKernel version %s' % ccmasterkernel.version())
        print('')

        if not ccmasterkernel.isLicenseValid():
            print("License error: ", ccmasterkernel.lastLicenseErrorMsg())
            sys.exit(0)

        # --------------------------------------------------------------------
        # create project
        # --------------------------------------------------------------------
        projectName = os.path.basename(self.projecDirPath)

        project = ccmasterkernel.Project()
        project.setName(projectName)
        project.setDescription('Automatically generated from python script')
        project.setProjectFilePath(os.path.join(self.projecDirPath, projectName))
        err = project.writeToFile()
        if not err.isNone():
            self.logger.info(err.message)
            sys.exit(0)

        self.logger.info('Project %s successfully created.' % projectName)
        print('')

        # --------------------------------------------------------------------
        # create block
        # --------------------------------------------------------------------
        block = ccmasterkernel.Block(project)
        project.addBlock(block)

        block.setName('block #1')
        block.setDescription('input block')
        photogroups = block.getPhotogroups()
        self.logger.info (self.photosDirPath)
        files = os.listdir(self.photosDirPath)

        for file in files:
            file = os.path.join(self.photosDirPath, file)

            # add photo, create a new photogroup if needed
            lastPhoto = photogroups.addPhotoInAutoMode(file)

            if lastPhoto is None:
                self.logger.info('Could not add photo %s.' % file)
                continue

            # upgrade block positioningLevel if a photo with position is found (GPS tag)
            if not lastPhoto.pose.center is None:
                block.setPositioningLevel(ccmasterkernel.PositioningLevel.PositioningLevel_georeferenced)

        print('')

        # check block
        self.logger.info('%s photo(s) added in %s photogroup(s):' % (photogroups.getNumPhotos(), photogroups.getNumPhotogroups()))

        photogroups = project.getBlock(0).getPhotogroups()

        for i_pg in range(0, photogroups.getNumPhotogroups()):
            self.logger.info('photogroup #%s:' % (i_pg + 1))
            if not photogroups.getPhotogroup(i_pg).hasValidFocalLengthData():
                self.logger.info('Warning: invalid photogroup')
            for photo_i in photogroups.getPhotogroup(i_pg).getPhotoArray():
                self.logger.info('image: %s' % photo_i.imageFilePath)
            print('')
          #  photogroups.getPhotogroup(i_pg).cameraModelBand = ccmasterkernel.CameraModelBand.CameraModelBand_visible
          #  photogroups.getPhotogroup(i_pg).CameraModelType = ccmasterkernel.CameraModelType.CameraModelType_perspective

           #  photogroups.getPhotogroup(i_pg).focalLength_mm = float(3.77202)
           #  photogroups.getPhotogroup(i_pg).focalLength35mm = float(22.938)
           #  mtx= ccmasterkernel.Matrix2()
           #  mtx.setElement(0, 0, float(5348.579647))
           #  mtx.setElement(1, 1, float(5348.579647))
           # # mtx.setElement(1, 1, float(5348.579647))
           #  photogroups.getPhotogroup(i_pg).fisheyeFocalMatrix = mtx
           #  photogroups.getPhotogroup(i_pg).principalPoint = ccmasterkernel.bindings.Point2d(2681.99, 1971.29)
           #  d = ccmasterkernel.FisheyeDistortion()
           #  d.p0 = float(0)
           #  d.p1 = float(1)
           #  d.p2 = float(0.483949)
           #  d.p3 = float(-0.724297)
           #  d.p4 = float(0)
           #  photogroups.getPhotogroup(i_pg).FisheyeDistortion = d
           #  print(photogroups.getPhotogroup(i_pg).cameraModelType)
        if not block.isReadyForAT():
            if block.reachedLicenseLimit():
                self.logger.info('Error: Block size exceeds license capabilities.')
                self.mm_project.status = "Error"
            if block.getPhotogroups().getNumPhotos() < 3:
                self.logger.info('Error: Insufficient number of photos.')
                self.mm_project.status = "Error"

            else:
                self.logger.info('Error: Missing focal lengths and sensor sizes.')
                self.mm_project.status = "Error"

            sys.exit(0)

        # --------------------------------------------------------------------
        # AT
        # --------------------------------------------------------------------
        blockAT = ccmasterkernel.Block(project)
        project.addBlock(blockAT)
        blockAT.setBlockTemplate(ccmasterkernel.BlockTemplate.Template_adjusted, block)

        err = project.writeToFile()
        if not err.isNone():
            self.logger.info(err.message)
            sys.exit(0)

        # Set some settings
        at_settings = blockAT.getAT().getSettings()
        at_settings.keyPointsDensity = ccmasterkernel.KeyPointsDensity.KeyPointsDensity_normal
        at_settings.splatsPreprocessing = ccmasterkernel.SplatsPreprocessing.SplatsPreprocessing_none
        at_settings.adjustmentConstraints = ccmasterkernel.AdjustmentAndPositioning.Positioning_PositionMetadata
        at_settings.loadPreset("configs/AT_preset.cfg")
        #turning off for thermal
       # at_settings.ColorEqualizationPreprocessing = ccmasterkernel.ColorEqualizationPreprocessing.ColorEqualizationPreprocessing_none


        if not blockAT.getAT().setSettings(at_settings):
            self.logger.info("Error: Failed to set settings for aerotriangulation")
            self.mm_project.status = "Error"

            sys.exit(0)
        atSubmitError = blockAT.getAT().submitProcessing()

        if not atSubmitError.isNone():
            self.logger.info('Error: Failed to submit aerotriangulation.')
            self.mm_project.status = "Error"

            self.logger.info(atSubmitError.message)
            sys.exit(0)

        self.logger.info('The aerotriangulation job has been submitted and is waiting to be processed...')

        iPreviousProgress = 0
        iProgress = 0
        previousJobStatus = ccmasterkernel.JobStatus.Job_unknown
        jobStatus = ccmasterkernel.JobStatus.Job_unknown

        while 1:
            jobStatus = blockAT.getAT().getJobStatus()

            if jobStatus != previousJobStatus:
                self.logger.info(ccmasterkernel.jobStatusAsString(jobStatus))

            if jobStatus == ccmasterkernel.JobStatus.Job_failed or jobStatus == ccmasterkernel.JobStatus.Job_cancelled or jobStatus == ccmasterkernel.JobStatus.Job_completed:
                break

            if iProgress != iPreviousProgress:
                self.logger.info('%s%% - %s' % (iProgress, blockAT.getAT().getJobMessage()))

            iPreviousProgress = iProgress
            iProgress = blockAT.getAT().getJobProgress()
            time.sleep(1)
            blockAT.getAT().updateJobStatus()
            previousJobStatus = jobStatus

        if jobStatus != ccmasterkernel.JobStatus.Job_completed:
            self.logger.info('"Error: Incomplete aerotriangulation.')
            self.mm_project.status = "Error"

            if blockAT.getAT().getJobMessage() != '':
                print(blockAT.getAT().getJobMessage())

        self.logger.info('Aerotriangulation completed.')

        if not blockAT.canGenerateQualityReport():
            self.logger.info("Error: BlockAT can't generate Quality report")
            sys.exit(0)
            self.mm_project.status = "Error"

        if not blockAT.generateQualityReport(True):
            self.logger.info("Error: failed to generate Quality report")
            self.mm_project.status = "Error"
            sys.exit(0)

       # self.logger.info("AT report available at", blockAT.getQualityReportPath())

        if not blockAT.isReadyForReconstruction():
            self.logger.info('Error: Incomplete photos. Cannot create reconstruction.')
            self.mm_project.status = "Error"
            sys.exit(0)

        self.logger.info('Ready for reconstruction.')

        if blockAT.getPhotogroups().getNumPhotosWithCompletePose_byComponent(1) < blockAT.getPhotogroups().getNumPhotos():
            self.logger.info('Warning: incomplete photos. %s/%s photo(s) cannot be used for reconstruction.' % (
            blockAT.getPhotogroups().getNumPhotos() - blockAT.getPhotogroups().getNumPhotosWithCompletePose_byComponent(1),
            blockAT.getPhotogroups().getNumPhotos()));

        # --------------------------------------------------------------------
        # Reconstruction
        # --------------------------------------------------------------------
        reconstruction = ccmasterkernel.Reconstruction(blockAT)
        reconsettings = reconstruction.getSettings()
        reconsettings.loadPreset("configs/Recons_preset.cfg")
        reconstruction.setSettings(reconsettings)
        blockAT.addReconstruction(reconstruction)

        if reconstruction.getNumInternalTiles() == 0:
            self.logger.info('Error: Failed to create reconstruction layout.')
            self.mm_project.status = "Error"
            sys.exit(0)

        self.logger.info('Reconstruction item created.')

        # --------------------------------------------------------------------
        # Production
        # --------------------------------------------------------------------
        production = ccmasterkernel.Production(reconstruction)

        reconstruction.addProduction(production)

        if self.cesium:
            production.setDriverName('Cesium 3D Tiles')
            production.setDestination(os.path.join(project.getProductionsDirPath(), production.getName()))
            driverOptions = production.getDriverOptions()
            self.logger.info(driverOptions)
            driverOptions.put_bool('TextureEnabled', True)
            driverOptions.put_int('TextureCompressionQuality', 75)
            driverOptions.writeXML(os.path.join(project.getProductionsDirPath(), "options.xml"))

        else:
            production.setDriverName('OBJ')	
            production.setDestination(os.path.join(project.getProductionsDirPath(), production.getName()))
            driverOptions = production.getDriverOptions()
            self.logger.info (driverOptions)
            driverOptions.put_bool('TextureEnabled', True)
            driverOptions.put_bool('DoublePrecision', True)
            driverOptions.put_int('TextureCompressionQuality', 75)
            driverOptions.put_int('MaximumTextureSize', 4096)
            #driverOptions.put_int('TextureColorSource', ccmasterkernel.CameraModelBand.CameraModelBand_thermal)
            #driverOptions.put_string('SRS', 'EPSG:32617')
            driverOptions.writeXML(os.path.join(project.getProductionsDirPath(), "options.xml"))

        production.setDriverOptions(driverOptions)

        self.logger.info('Production item created.')

        productionSubmitError = production.submitProcessing()

        if not productionSubmitError.isNone():
            self.logger.info('Error: Failed to submit production.')
            self.mm_project.status = "Error"
            self.logger.info(productionSubmitError.message)
            sys.exit(0)

        self.logger.info('The production job has been submitted and is waiting to be processed...')
        iPreviousProgress = 0
        iProgress = 0
        previousJobStatus = ccmasterkernel.JobStatus.Job_unknown

        while 1:
            jobStatus = production.getJobStatus()

            if jobStatus != previousJobStatus:
                self.logger.info(ccmasterkernel.jobStatusAsString(jobStatus))

            if jobStatus == ccmasterkernel.JobStatus.Job_failed or jobStatus == ccmasterkernel.JobStatus.Job_cancelled or jobStatus == ccmasterkernel.JobStatus.Job_completed:
                break

            if iProgress != iPreviousProgress:
                self.logger.info('%s%% - %s' % (iProgress, production.getJobMessage()))

            iPreviousProgress = iProgress
            iProgress = production.getJobProgress()
            time.sleep(1)
            production.updateJobStatus()
            previousJobStatus = jobStatus

        self.logger.info('')

        if jobStatus != ccmasterkernel.JobStatus.Job_completed:
            self.logger.info('"Error: Incomplete production.')
            self.mm_project.status = "Error"
            if production.getJobMessage() != '':
                self.logger.info(production.getJobMessage())

        # --------------------------------------------------------------------
        # Report
        # --------------------------------------------------------------------
        self.logger.info('Production completed.')
        self.logger.info('Output directory: %s' % production.getDestination())

        with open(production.getDestination() + '/metadata.xml',
                  'r+') as f:
            xml_string = f.read()

        root = ET.fromstring(xml_string)

        # Extract the attributes and values of the XML elements as key-value pairs
        metadata = {}
        for child in root:
            metadata[child.tag] = child.text

        # Print the resulting dictionary

        # path to the input OBJ file
        input_file = production.getDestination() + "/Data/Model/Model.obj"

        # path to the output folder
        output_folder = production.getDestination() + "/Data/Model/"
        zip_location = production.getDestination() + "/Data/"
        # create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        x = str(eval(str(metadata['SRSOrigin'])[0]))
        y = str(eval(metadata['SRSOrigin'])[1])
        z = str("101.000")
        with open(output_folder + "/metadata.xyz",
                  'w') as xyz:
            xyz.write(x + " " + y + " " + z)
        shutil.copy("configs/WGS84.prj", production.getDestination()  + "/Data/Model/metadata.prj")


        # set the output file name based on the input file name
        output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + ".obj")

        # # create a MeshSet object and load the input OBJ file
     #   ms = pymeshlab.MeshSet()
     #   ms.load_new_mesh(input_file)
        # # save the MeshSet object to the output file
     #   ms.save_current_mesh(output_file)
        inp_folder = production.getDestination() + "/Data/"
        #shutil.copytree(inp_folder, output_folder + "/")
        # print a message when the process is complete
        self.logger.info("Output file saved to:" + output_file)
        self.logger.info("Filename:" + self.filename[:len(self.filename)-4])
        self.logger.info("Output folder:" + output_folder)
        a = os.path.join(zip_location + self.filename)
        self.logger.info ("Zip filename path : " + a)
        if len(self.filename) > 19:
            shutil.make_archive(zip_location+self.filename[:len(self.filename)-4], 'zip', inp_folder)
            self.logger.info("cutting filename")
        else:
            shutil.make_archive(zip_location+self.filename, 'zip', production.getDestination() + "/Data/Model/")
        if ".zip" in a:
            self.logger.info("already has .zip in upload filename")
        else:
            a = a + ".zip"
        self.mm_project.time_processing_complete = time.time()
        self.logger.info ("Sending zip file to ARTAK Content Repository. File = " + str(a))

        # rename zip if manually set
        if self.mm_project.manually_made_name:
            if self.mm_project.manually_made_name != "":
                manually_set_filename = self.mm_project.manually_made_name + ".zip"
                new_path = os.path.join(zip_location, manually_set_filename)
                self.logger.info("Name has been set manually. Name = " + manually_set_filename)
                self.logger.info("New Path = " + new_path)
                self.logger.info("Renaming " + a + " to " + new_path)
                os.rename(a, new_path)
                a = new_path
        if self.cesium:
            self.logger.info("Not Sending Cesium Tile Anywhere")
            #Todo add upload to cesium
        else:
            try:
                self.logger.info("Attempting to upload " + a + " to " + str(self.artak_server))
                response = self.upload(a, url=self.artak_server)
                self.logger.info(response.status_code)
                if response.status_code == 200:
                    self.mm_project.time_accepted_by_artak = time.time()
                    self.mm_project.status = "Complete"
                else:
                    self.mm_project.status = "Error"
                self.logger.info(self.mm_project)
            except:
                self.logger.info("Uncaught exception attempting to upload file. File = " + str(a) + "URL = " + self.artak_server)
        return self.mm_project.status
#supload("C:/ARTAK_MM/POST/Photogrammetry/Ztest5.zip388\Productions\Production_1/Data/Model/Preprocessed" + "/" + "Ztest5.zip" + ".zip")
#upload("C:/ARTAK_MM/POST/Photogrammetry/2023-06-13_18-26-02921/Productions/Production_1/Data/Model/2023-06-13_18-2.zip")
##a = processing_photogrammetry('Ztest.zip', MM__logger.initialize_logger())
#a.do_photogrammetry()
