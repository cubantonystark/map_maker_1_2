# importing the zipfile module
import os
from zipfile import ZipFile
import shutil
import MM_logger
from MM_processing_photogrammetry import ProcessingPhotogrammetry
# UNZIP
# DO PRE-PROCESSING -- coming soon
# PROCESS
# SEND TO APPROPRIATE REPOSITORY

class MMfileHandler:

	def __init__(self, file_name, logger):


		self.source_zip = file_name
		self.destination_path = os.getcwd()+"/ARTAK_MM/DATA/Raw_Images/UNZIPPED/" + self.source_zip.replace(".zip", "")
		self.source_path = os.getcwd()+"/ARTAK_MM/DATA//Raw_Images/ZIP/New/" + self.source_zip
		self.in_progress_path = os.getcwd()+"/ARTAK_MM/DATA/Raw_Images/ZIP/Unzipping_in_progress/" + self.source_zip
		self.completed_path = os.getcwd()+"/ARTAK_MM/DATA/Raw_Images/ZIP/Completed/" + self.source_zip
		self.logger = logger

	def unzip(self):

		self.logger.info("Beginning unzip method. Filename = " + self.source_zip)
		self.logger.info("Moving source file to in progress folder. Filename = " + self.source_zip)
		shutil.move(self.source_path,  self.in_progress_path)
		self.logger.info("Unzipping file from in progress folder." + self.source_zip)
		with ZipFile(self.in_progress_path, 'r') as zObject:
			# Extracting all the members of the zip
			# into a specific location.
			zObject.extractall(
				path=self.destination_path
		)
		self.logger.info("Moving file from in progress folder to completed folder.Filename =" + self.source_zip)
		shutil.move(self.in_progress_path, self.completed_path)
		self.logger.info("Unzip Complete. Filename =" + self.source_zip)

