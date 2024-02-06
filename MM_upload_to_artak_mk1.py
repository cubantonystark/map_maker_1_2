import requests


def login(url):
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
    print(response)
    if response["status"] == 'Success':
        session_token = str(response["data"])
    print(session_token)
    return session_token


def upload_to_artak_server(file_dict: dict, data: dict, url):
    upload_url = url + "dit/v1/"
    session_token = login(url)
    print("login url = " + url)
    print("upload url = " + upload_url)
    r = requests.post(
        upload_url + "upload",
        data=data,
        headers={"x-api-key": session_token},
        files=file_dict,
    )
    return r


# method to upload a file to the server
def upload(the_file, url="https://esp.eastus2.cloudapp.azure.com/"):

    if the_file is None:
        pass

    else:

        print(the_file)
        print("Sending the file =" + the_file)
        file_zip = open(the_file, "rb")
        payload = {"file": file_zip}
        params = {"type": "maps"}
        print("url : " + url)
        response = upload_to_artak_server(file_dict=payload, data=params, url=url)
        print(response)
        return response

# example usage

# file = "C:/Users/micha/Apps/MapMaker4/map_maker_1_2/ARTAK_MM/POST/Photogrammetry/lr_TE_warehouse_interior/Productions/Production_1/Data/Mode/lr_TE_warehouse_interior.zip"
# file = "C:/Users/micha/OneDrive/Desktop/lr_TE_warehouse_interior.zip"
# upload(file, url="https://esp.eastus2.cloudapp.azure.com/")