import os
import json


class MapmakerProject:
    def __init__(self, name=None, time_first_image=None, time_mm_start=None, time_processing_start=None,
                 time_processing_complete=None, time_accepted_by_artak=None, total_images=None, image_folder=None,
                 processed_zip_path=None, status=None, logger=None, artak_server=None, manually_made_name=None,
                 manually_made_name_field=None, local_image_folder=None, session_project_number=None,
                 completed_file_path=None, map_type=None, zip_payload_location=None, total_processing_time=None,
                 partition_key=None, quality=None):
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
        self.total_processing_time = total_processing_time
        self.partition_key = partition_key
        self.quality = quality
    def as_dict(self):
        return vars(self)

    def upload_to_world(self):
        os.system(
            r'curl -F uploadFile=@' + self.zip_payload_location + ' -F partition_key=' + self.partition_key + ' https://resqview.eastus2.cloudapp.azure.com/api/upload-tileset -H "Content-Type: multipart/form-data"')


def load_settings():
    with open('./MM_settings.txt', 'r') as file:
        lines = file.readline()
        settings_json = json.loads(lines)
        payload = settings_json["mm_settings"]
    return payload


class MapmakerSettings:

    def __init__(self):
        super().__init__()
        self.artak_server = ""
        self.map_type = ""
        self.auto_process_sd = ""
        self.mesh_from_pointcloud_type = ""
        self.rerun_failed_jobs = ""
        self.local_server_ip = ""
        self.max_interval_between_images = ""
        self.app_screen_mode = ""
        self.delete_after_transfer = ""
        self.auto_open_upon_completion = ""

    def save(self):
        mm_settings = {'mm_settings': vars(self)}

        with open('MM_settings.txt', 'w') as file:
            file.write(json.dumps(mm_settings))  # use `json.loads` to do the reverse

