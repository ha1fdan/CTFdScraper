import os
from dotenv import load_dotenv
load_dotenv()
import requests
import argparse
import sys
import os
from bs4 import BeautifulSoup

# Command-line argument parsing
parser = argparse.ArgumentParser(description="CTFd Scraper - Download challenges and files")
parser.add_argument("--username", help="CTFd username")
parser.add_argument("--password", help="CTFd password")
parser.add_argument("--session", help="Session cookie for CTFd")
parser.add_argument("--url", default="https://icoblue2025.ctfd.io", help="Base URL of the CTFd instance")
args = parser.parse_args()

url = args.url.rstrip("/")

# If session cookie is provided, use it directly
if args.session:
    print("[+] Using session cookie")
    cookies = {
        'session': args.session,
    }
else:
    # Require username and password if session is not provided
    if not args.username or not args.password:
        print("[-] Either --session or both --username and --password are required.")
        exit(1)
    else:
        login_url = f"{url}/login"
        session = requests.Session()
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.text, "html.parser")
        nonce = soup.find("input", {"name": "nonce"})["value"]
        data = {"name": args.username,"password": args.password,"nonce": nonce}
        response = session.post(login_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, allow_redirects=False)
        cookies = session.cookies.get_dict()

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (X11; TempleOS x86_32; rv:139.0) Gecko/20100101 Firefox/139.0'
}

###### GET CHALLENGES ######
challenges_url = f'{url}/api/v1/challenges'
response = requests.get(challenges_url, headers=headers, cookies=cookies)
if response.status_code == 200:
    challenges = response.json()['data']
    print("Challenges retrieved successfully.")
else:
    if response.status_code == 403:
        print(response.text)
        print("Access forbidden. Challenges may not be available yet or your session may have expired.")
        sys.exit(1)
    else:
        print(f"Failed to retrieve challenges: {response.status_code} - {response.text}")
        sys.exit(1)

###### GET FILES AND DOWNLOAD ######
for challenge in challenges:
    chall_data = requests.get(f"{url}/api/v1/challenges/{challenge['id']}", cookies=cookies, headers=headers)
    if chall_data.status_code != 200:
        print(f"Failed to retrieve challenge data for {challenge['id']}: {chall_data.status_code} - {chall_data.text}")
        continue
    
    chall_data = chall_data.json()['data']
        
    # Create output directory if it doesn't exist
    path=os.path.join("output",chall_data['category'],chall_data['name'])
    os.makedirs(path, exist_ok=True)
        
    ### Make description.md file
    description_path = os.path.join(path, "description.md")
    with open(description_path, "w") as desc_file:
        desc_file.write(f"# {chall_data['name']}\n\n")
        desc_file.write(f"## Description\n{chall_data['description']}\n\n")
        desc_file.write(f"## Category\n{chall_data['category']}\n\n")
        desc_file.write(f"## Points\n{chall_data['value']}\n\n")
    
    for file in chall_data['files']:
        file_data = requests.get(f"{url}{file}", headers=headers, cookies=cookies)
        if file_data.status_code == 200:
            file_name = os.path.basename(file.split('?')[0])
            file_path = os.path.join(path, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_data.content)
            print(f"Downloaded {file_name} for challenge {challenge['name']}.")
        else:
            print(f"Failed to download {file} for challenge {challenge['name']}: {file_data.status_code} - {file_data.text}")
            continue