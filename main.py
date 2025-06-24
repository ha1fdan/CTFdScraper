import os
from dotenv import load_dotenv
load_dotenv()
import requests


url = os.getenv('URL')
token = os.getenv('TOKEN')
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0'
}

def listChallenges():
    url = os.getenv('URL')
    token = os.getenv('TOKEN')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:139.0) Gecko/20100101 Firefox/139.0'
    }
    response = requests.get(f'{url}/api/v1/files', headers=headers)
    return response.json()

#try make output dir
os.mkdir("output")
files =listChallenges()
for fille in files["data"]:
    path= os.getenv('URL')+"/files/"+str(fille["location"])
    r=requests.get(path, headers=headers)
    filename="output/"+fille["location"].split("/")[-1]
    with open(filename, "wb") as f:
        f.write(r.content)