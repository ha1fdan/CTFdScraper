import os
from dotenv import load_dotenv
load_dotenv()
import requests


url = os.getenv('URL')
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; TempleOS x86_32; rv:139.0) Gecko/20100101 Firefox/139.0'
}
cookies = {
    'session': os.getenv('SESSION'),
}

###### GET CHALLENGES ######
challenges_url = f'{url}/api/v1/challenges'
response = requests.get(challenges_url, headers=headers, cookies=cookies)
if response.status_code == 200:
    challenges = response.json()['data']
    #print("Challenges retrieved successfully.")
else:
    print(f"Failed to retrieve challenges: {response.status_code} - {response.text}")
    
print("Challenges:", challenges)

###### GET FILES AND DOWNLOAD ######
for challenge in challenges:
    file_url = f"{url}/api/v1/challenges/{challenge['id']}/files"
    files= requests.get(file_url, headers=headers, cookies=cookies)
    if files.status_code == 200:
        files_data = files.json()['data']
        print(f"Files for challenge {challenge['id']} retrieved successfully.")
        
        # Create output directory if it doesn't exist
        path=os.path.join("output",challenge['category'],challenge['name'])
        os.makedirs(path, exist_ok=True)
        
        ### Make description.md file
        description_path = os.path.join(path, "description.md")
        with open(description_path, "w") as desc_file:
            chall_data = requests.get(f"{url}/api/v1/challenges/{challenge['id']}", headers=headers, cookies=cookies)
            if chall_data.status_code == 200:
                chall_data_json = chall_data.json()['data']
                desc_file.write(f"# {chall_data_json['name']}\n\n")
                desc_file.write(f"## Description\n{chall_data_json['description']}\n\n")
                desc_file.write(f"## Category\n{challenge['category']}\n\n")
                desc_file.write(f"## Points\n{chall_data_json['value']}\n\n")
        
        for filee in files_data:
            file_path = f"{url}/files/{filee['location']}"
            r = requests.get(file_path, headers=headers, cookies=cookies)
            if r.status_code == 200:
                filename = os.path.join(path,filee['location'].split("/")[-1])
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed to download file {filee['location'].split("/")[-1]}: {r.status_code} - {r.text}")