import os


class MapmakerProject:
    def __init__(self, name=None, time_first_image=None, time_mm_start=None, time_processing_start=None,
                 time_processing_complete=None, time_accepted_by_artak=None, total_images=None, image_folder=None,
                 processed_zip_path=None, status=None, logger=None, artak_server=None, manually_made_name=None,
                 manually_made_name_field=None, local_image_folder=None, session_project_number=None,
                 completed_file_path=None, map_type=None, zip_payload_location=None):
        self.name = name
        self.time_first_image = time_first_image
        self.time_mm_start = time_mm_start
        self.time_processing_start = time_processing_start
        self.time_processing_complete = time_processing_complete
        self.time_accepted_by_artak = time_accepted_by_artak
        self.total_images = total_images
        self.image_folder = image_folder
        self.processed_zip_path = processed_zip_path
        self.status = status
        self.logger = logger
        self.artak_server = artak_server
        self.manually_made_name = manually_made_name
        self.manually_made_field = manually_made_name_field
        self.local_image_folder = local_image_folder
        self.session_project_number = session_project_number
        self.completed_file_path = completed_file_path
        self.map_type = map_type # ces for cesium tiles or obj for obj files
        self.zip_payload_location = zip_payload_location

    def as_dict(self):
        return vars(self)

    def upload_to_world(self):
        os.system(
            r'curl -F uploadFile=@' + self.zip_payload_location + ' -F partition_key= https://resqview.eastus2.cloudapp.azure.com/api/upload-tileset -H "Content-Type: multipart/form-data"')


