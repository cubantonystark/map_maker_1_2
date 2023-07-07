import requests

url = 'http://192.168.1.16:8080/upload'
filepath = "C:/Users/micha/Documents/PhotogrammetryDataSets/PuertoRico.zip"

with open(filepath, 'rb') as f:
    response = requests.post(url, files={'file': f})

print(response.status_code)