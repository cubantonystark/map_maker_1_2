# importing the zipfile module
import os
from zipfile import ZipFile
import shutil
import MM_video


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
		"""
		Unzips file and if the file contains a video extract the frames from the video

		Returns:
		Destination path for the data after unzipping/extracting frames
		"""
		self.logger.info("Beginning unzip method. Filename = " + self.source_zip)
		self.logger.info("Moving source file to in progress folder. Filename = " + self.source_zip)
		shutil.move(self.source_path,  self.in_progress_path)
		self.logger.info("Unzipping file from in progress folder." + self.source_zip)
		count = 1
		if os.path.exists(self.destination_path + "-V" + str(count)):
			duplicate_file = True
			while duplicate_file:
				count += 1
				if os.path.exists(self.destination_path + "-V" + str(count)):
					duplicate_file = True
				else:
					self.destination_path = self.destination_path + "-V" + str(count)
					duplicate_file = False
		else:
			self.destination_path = self.destination_path + "-V" + str(count)

		with ZipFile(self.in_progress_path, 'r') as zObject:
			# Extracting all the members of the zip
			# into a specific location.
			zObject.extractall(
				path=self.destination_path
		)
		self.logger.info("Moving file from in progress folder to completed folder.Filename =" + self.source_zip)
		shutil.move(self.in_progress_path, self.completed_path)
		self.logger.info("Unzip Complete. Filename =" + self.source_zip)

		# handle different data types
		# set variables
		video_found = False
		video = ""
		lidar_found = False
		lidar = ""
		lidar_extensions = ['.ply', '.pts', '.e57']
		video_extensions = ['.mpeg', '.mp4', '.ts', ".m4v"]  # Add more extensions if needed

		for i in os.listdir(self.destination_path):
			for each_extension in video_extensions:
				if each_extension in i:
					video_found = True
					video = i
			for each_extension in lidar_extensions:
				if each_extension in i:
					lidar_found = True
					lidar = i

		# handle video
		if video_found:
			video_file_name = str(os.path.basename(video))
			# remove .mp4 from filename
			video_name = video_file_name.split(".")[0]
			# cleanup filename
			video_name_nospaces = video_name.replace(" ", "_")
			video_name_nospaces_noperiods = video_name_nospaces.replace(".", "-")
			# extract the frames from the video
			video_name = MM_video.extract_frames(os.path.join(self.destination_path, video), self.destination_path, frame_spacing=int(10))
			# add the path of the extracted frames to the folder paths array to be returned to mapmaker for processing

		# handle lidar
		if lidar_found:
			print ('lidar')
			print ('lidar')
		try:
			return self.destination_path
		except:
			return self.source_zip.replace(".zip", "")

