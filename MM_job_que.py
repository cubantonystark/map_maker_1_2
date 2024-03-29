import os
import json
import MM_objects


def write_dict_to_file(dict_data):
    try:
        file_name = os.path.join(os.getcwd(), "job-que.txt")
        with open(file_name, 'w') as file:
            json.dump({'test': dict_data}, file, indent=4)
        print(f"Dictionary written to {file_name} in JSON format.")
    except IOError as e:
        print(f"An error occurred: {e}")


def update_mm_project_in_file(mm_project):
    dict_data = mm_project.as_dict()
    update_dict_in_file(dict_data)


def update_dict_in_file(dict_data):
    key = dict_data["name"]
    # open dict from file
    current_que = read_job_que_from_json_file()
    file_name = os.path.join(os.getcwd(), "job-que.txt")
    try:
        current_que[key] = dict_data
        with open(file_name, 'w') as file:
            json.dump(current_que, file, indent=4)
    except:
        print ("error updating dict")

    # replace dict for key matching dict_data


def save_mm_project(mm_project):
    destination = mm_project.zip_payload_location
    file_name = destination + "-MM_Project.txt"
    with open(file_name, 'w') as file:
        json.dump(mm_project.as_dict(), file, indent=4)
    print("saved")


def remove_project_in_file(mm_project):
    key = mm_project.name
    # open dict from file
    current_que = read_job_que_from_json_file()
    file_name = os.path.join(os.getcwd(), "job-que.txt")
    mm_project_payload = current_que[key]
    save_mm_project(mm_project)
    try:
        current_que.pop(key)
        with open(file_name, 'w') as file:
            json.dump(current_que, file, indent=4)
    except:
        print ("error updating dict")


def add_job_to_que(new_mm_project):
    update_dict_in_file(new_mm_project.as_dict())

def clear_job_que():
    file_name = os.path.join(os.getcwd(), "job-que.txt")

    try:
        file = open(file_name, 'w')
        file.writelines("{}")
        file.close()
    except IOError as e:
        print(f"An bit of an error occurred while reading the file: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON: {e}")
        return None

def read_job_que_from_json_file():
    file_name = os.path.join(os.getcwd(), "job-que.txt")
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            return data
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON: {e}")
        return None

def read_job_que_from_json_file_return_mm_objects():
    #print ("MM_job_que.py logs. Current Working Directory:", os.getcwd())
    file_name = os.path.join(os.getcwd(), "job-que.txt")
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            mm_objects = MM_objects.projects_from_dict(data)
            return mm_objects
    except IOError as e:
        print(f"An error occurred while reading the file to return mm objectsx: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"An error occurred while decoding JSON: {e}")
        return None

# Example Usage
#my_dict = read_job_que_from_json_file()
#add_job_to_que()



