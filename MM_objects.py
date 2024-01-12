import os
import json
import MM_job_que


class MapmakerProject:

    def __init__(self, name=None, time_first_image=None, time_mm_start=None, time_processing_start=None,
                 time_processing_complete=None, time_accepted_by_artak=None, total_images=None, image_folder=None,
                 processed_zip_path=None, status=None, logger=None, artak_server=None, manually_made_name=None,
                 manually_made_name_field=None, local_image_folder=None, session_project_number=None,
                 completed_file_path=None, map_type=None, zip_payload_location=None, total_processing_time=None,
                 partition_key=None, quality=None, video_frame_extraction_rate=None, data_type=None):
        self.name = name
        self.data_type = data_type
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
        self.video_frame_extraction_rate = video_frame_extraction_rate


    def set_type(self, var):
        self.type = var
        MM_job_que.update_mm_project_in_file(self)


    def set_local_image_folder(self, var):
        self.local_image_folder = var
        MM_job_que.update_mm_project_in_file(self)

    def set_partition_key(self, var):
        self.partition_key = var
        MM_job_que.update_mm_project_in_file(self)

    def set_time_processing_start(self, var):
        self.time_processing_start = var
        MM_job_que.update_mm_project_in_file(self)

    def set_time_processing_complete(self, var):
        self.time_processing_complete = var
        MM_job_que.update_mm_project_in_file(self)

    def set_time_accepted_by_artak(self, var):
        self.time_accepted_by_artak = var
        MM_job_que.update_mm_project_in_file(self)

    def set_processed_zip_path(self, var):
        self.processed_zip_path = var
        MM_job_que.update_mm_project_in_file(self)

    def set_status(self, var):
        self.status = var
        MM_job_que.update_mm_project_in_file(self)
        if var == "complete":
            MM_job_que.remove_project_in_file(self)


    def set_artak_server(self, var):
        self.artak_server = var
        MM_job_que.update_mm_project_in_file(self)

    def set_manually_made_name(self, var):
        self.manually_made_name = var
        MM_job_que.update_mm_project_in_file(self)

    def set_completed_file_path(self, var):
        self.completed_file_path = var
        MM_job_que.update_mm_project_in_file(self)

    def set_zip_payload_location(self, var):
        self.zip_payload_location = var
        MM_job_que.update_mm_project_in_file(self)

    def set_total_processing_time(self, var):
        self.total_processing_time = var
        MM_job_que.update_mm_project_in_file(self)

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



def projects_from_dict(dictionary):
    projects = []
    for each_project in dictionary.keys():
        proj = project_from_dict(dictionary[each_project])
        projects.append(proj)
    return projects


def project_from_dict(dictionary):
    mm_project = MapmakerProject()
    mm_project.name = dictionary['name']
    mm_project.data_type = dictionary['data_type']
    mm_project.time_first_image = dictionary['time_first_image']
    mm_project.time_mm_start = dictionary['time_mm_start']
    mm_project.time_processing_start = dictionary['time_processing_start']
    mm_project.time_processing_complete = dictionary['time_processing_complete']
    mm_project.time_accepted_by_artak = dictionary['time_accepted_by_artak']
    mm_project.total_images = dictionary['total_images']
    mm_project.image_folder = dictionary['image_folder']
    mm_project.processed_zip_path = dictionary['processed_zip_path']
    mm_project.status = dictionary['status']
    mm_project.logger = "na"
    mm_project.artak_server = dictionary['artak_server']
    mm_project.manually_made_name = dictionary['manually_made_name']
    # mm_project.manually_made_field = dictionary['manually_made_name_field']
    mm_project.local_image_folder = dictionary['local_image_folder']
    mm_project.session_project_number = dictionary['session_project_number']
    mm_project.completed_file_path = dictionary['completed_file_path']
    mm_project.map_type = dictionary['map_type']  # ces for cesium tiles or obj for obj files
    mm_project.zip_payload_location = dictionary['zip_payload_location']
    mm_project.total_processing_time = dictionary['total_processing_time']
    mm_project.partition_key = dictionary['partition_key']
    mm_project.quality = dictionary['quality']
    return mm_project


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

