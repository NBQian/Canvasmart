import requests
import json
from datetime import datetime
import os
import json

config = {}

CONFIG_FILE = "config.json"


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


base_url = "https://canvas.nus.edu.sg/api/v1"


def is_token_expired(token):
    h = {"Authorization": f"Bearer {token}"}
    test_url = f"{base_url}/courses"
    response = requests.get(test_url, headers=h)

    if response.status_code == 401 or response.status_code == 403:
        if "token is expired" in response.text:
            return True
        return False
    elif response.status_code == 200:
        return False
    else:
        print(f"Unexpected response code: {response.status_code}")
        return False


def get_paginated_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(json.loads(response.text))
            link_header = response.headers.get("Link", None)
            if link_header:
                links = link_header.split(",")
                next_link = [l.split(";")[0] for l in links if 'rel="next"' in l]
                url = next_link[0][1:-1] if next_link else None
            else:
                url = None
        else:
            break
    return all_data


def get_course_files(course_id):
    course_files_url = f"{base_url}/courses/{course_id}/files"
    return get_paginated_data(course_files_url)


def get_folders(parent_type, parent_id):
    folders_url = f"{base_url}/{parent_type}/{parent_id}/folders"
    return get_paginated_data(folders_url)


def get_files(folder_id):
    files_url = f"{base_url}/folders/{folder_id}/files"
    return get_paginated_data(files_url)


def get_courses(course_names):
    courses_url = f"{base_url}/courses"
    all_courses = get_paginated_data(courses_url)

    valid_courses = []
    for course in all_courses:
        if "created_at" in course:
            if course["name"].endswith(config["semester"]):
                valid_courses.append(course)
    if course_names != None:
        return [course for course in valid_courses if course["name"][:6] in course_names]        
    return valid_courses


def get_modules(course_id):
    modules_url = f"{base_url}/courses/{course_id}/modules"
    return get_paginated_data(modules_url)


def get_module_items(course_id, module_id):
    items_url = f"{base_url}/courses/{course_id}/modules/{module_id}/items"
    return get_paginated_data(items_url)


def download_file(url, destination_path):
    with requests.get(url, stream=True, headers=headers) as response:
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_files_for_module(course_id, module_id, module_path):
    items = get_module_items(course_id, module_id)
    for item in items:
        if item["type"] == "File":
            download_file(item["url"], os.path.join(module_path, item["display_name"]))


def download_files_in_folder(folder_id, destination_path):
    subfolders = get_folders("folders", folder_id)
    for subfolder in subfolders:
        if subfolder["name"] == "unfiled":
            continue
        subfolder_path = os.path.join(destination_path, subfolder["name"])
        os.makedirs(subfolder_path, exist_ok=True)
        download_files_in_folder(subfolder["id"], subfolder_path)

    files = get_files(folder_id)
    for file in files:
        download_file(file["url"], os.path.join(destination_path, file["display_name"]))


def download_files_by_modules(course_id, course_path):
    modules = get_modules(course_id)
    for module in modules:
        module_path = os.path.join(course_path, module["name"])
        os.makedirs(module_path, exist_ok=True)

        items = get_module_items(course_id, module["id"])
        for item in items:
            if item["type"] == "File":
                download_file(item["url"], os.path.join(module_path, item["title"]))


def has_course_files(course_id):
    response = requests.get(f"{base_url}/courses/{course_id}/files", headers=headers)
    return response.status_code == 200


def download_files_for_course(course_id, course_path):
    if has_course_files(course_id):
        folders = get_folders("courses", course_id)
        for folder in folders:
            if folder["name"] == "course files":
                download_files_in_folder(folder["id"], course_path)
                break
    else:
        download_files_by_modules(course_id, course_path)


def download_all(course_names = None):
    root_folder = config["download_path"]

    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
    courses = get_courses(course_names)
    for course in courses:
        course_path = os.path.join(root_folder, course["name"][:6])

        if not os.path.exists(course_path):
            os.makedirs(course_path)
        download_files_for_course(course["id"], course_path)

def download_for_courses(course_names):
    download_all(course_names)


def display_folders_and_files(folder_id, indentation=0):
    files = get_paginated_data(f"{base_url}/folders/{folder_id}/files")
    for file in files:
        print(" " * indentation + file["display_name"])

    folders = get_paginated_data(f"{base_url}/folders/{folder_id}/folders")
    for folder in folders:
        if folder["name"] == "unfiled":
            continue
        print(" " * indentation + folder["name"])
        print(" " * indentation + "\\" + "-" * len(folder["name"]) + "/")
        display_folders_and_files(folder["id"], indentation + 4)


def display_files_by_modules(course_id, indentation=4):
    modules = get_paginated_data(f"{base_url}/courses/{course_id}/modules")
    for module in modules:
        print(" " * indentation + module["name"])
        print(" " * indentation + "\\" + "-" * len(module["name"]) + "/")
        items = get_paginated_data(
            f"{base_url}/courses/{course_id}/modules/{module['id']}/items"
        )
        for item in items:
            if item["type"] == "File":
                print(" " * (indentation + 4) + item["title"])


def list_all():
    courses = get_paginated_data(f"{base_url}/courses")
    for course in courses:
        if "name" in course and course["name"].endswith(config["semester"]):
            print("=" * len(course["name"]))
            print(course["name"])
            print("=" * len(course["name"]))

            if has_course_files(course["id"]):
                folders = get_paginated_data(
                    f"{base_url}/courses/{course['id']}/folders"
                )
                course_files_folder = next(
                    (folder for folder in folders if folder["name"] == "course files"),
                    None,
                )
                if course_files_folder:
                    display_folders_and_files(course_files_folder["id"], 4)
            else:
                print("    No 'files' section found. Checking 'Modules'...")
                display_files_by_modules(course["id"])

def get_existing_files(download_path):
    existing_files = set()
    for root, dirs, files in os.walk(download_path):
        for filename in files:
            existing_files.add(filename)
    return existing_files


def list_new(dic):
    existing_files = get_existing_files(config["download_path"])
    
    courses = get_paginated_data(f"{base_url}/courses")
    for course in courses:
        if "name" in course and course["name"].endswith(config["semester"]):
            course_path = os.path.join(config["download_path"], course["name"][:6])
            if not os.path.exists(course_path):
                os.makedirs(course_path)
            print("=" * len(course["name"]))
            print(course["name"])
            print("=" * len(course["name"]))

            new_files_found = False

            if has_course_files(course["id"]):
                folders = get_paginated_data(f"{base_url}/courses/{course['id']}/folders")
                course_files_folder = next((folder for folder in folders if folder["name"] == "course files"), None)
                
                if course_files_folder:
                    new_files_found, new_files = display_new_files_in_folders(course_files_folder["id"], 4, existing_files, course_path, dic)

                    if new_files_found:
                        for file in new_files:
                            print(" " * 4 + file)
            else:
                print("    No 'files' section found. Checking 'Modules'...")
                new_files_found = display_new_files_by_modules(course["id"], existing_files, 4, course_path, dic)

            if not new_files_found:
                print("    Your local files are up to date!")


def display_new_files_in_folders(folder_id, indentation, existing_files, local_path, dic):
    new_files_found = False
    new_file_names = []
    
    files = get_paginated_data(f"{base_url}/folders/{folder_id}/files")
    new_files = [f for f in files if f["display_name"] not in existing_files]
    
    if new_files:
        new_files_found = True
        for file in new_files:
            new_file_path = os.path.join(local_path, file["display_name"])
            dic[file["display_name"]] = {
                'url': file['url'],
                'local_path': new_file_path
            }
            new_file_names.append(file["display_name"])
            
    folders = get_paginated_data(f"{base_url}/folders/{folder_id}/folders")
    for folder in folders:
        if folder["name"] == "unfiled":
            continue
        new_folder_path = os.path.join(local_path, folder["name"])
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        folder_has_new_files, subfolder_new_files = display_new_files_in_folders(folder["id"], indentation + 4, existing_files, new_folder_path, dic)
        
        if folder_has_new_files:
            print(" " * indentation + folder["name"])
            print(" " * indentation + "\\" + "-" * len(folder["name"]) + "/")
            for subfile in subfolder_new_files:
                print(" " * (indentation + 4) + subfile)
            new_files_found = True
            
    return new_files_found, new_file_names



def display_new_files_by_modules(course_id, existing_files, indentation, local_path, dic):
    modules = get_paginated_data(f"{base_url}/courses/{course_id}/modules")
    
    new_files_found = False

    for module in modules:
        items = get_paginated_data(
            f"{base_url}/courses/{course_id}/modules/{module['id']}/items"
        )
        new_items = [item for item in items if item["type"] == "File" and item["title"] not in existing_files]

        if new_items:
            new_files_found = True
            print(" " * indentation + module["name"])
            print(" " * indentation + "\\" + "-" * len(module["name"]) + "/")
            for item in new_items:
                file_data = get_paginated_data(f"{base_url}/courses/{course_id}/files/{item['content_id']}")          
                local_path = os.path.join(module_path, file_data["display_name"])
                new_files_dict[file_data["display_name"]] = {
                    'url': file_data['url'],
                    'local_path': local_path
                }
                print(" " * (indentation + 4) + item["title"])

    return new_files_found

def download_new(dic):
    for file_name, file_info in dic.items():
        download_file(file_info['url'], file_info['local_path'])

def display_help_msg():
    print("List of available commands:")
    print("  - download all: Download all courses' materials")
    print("  - download new: Download new files")
    print("  - download for <course name1> <course name2> ... : Download materials for specified courses")
    print("  - list all: List all files available for download")
    print("  - list new: List new files available for download")
    print("  - exit: Exit the program")
    print("  - help: Display this help message")

def display_error_msg():
    print("Instruction not recognized. Please enter a valid command.")

def welcome():
    print("Welcome to the Canvas File Management Tool!")
    print("This tool will help you efficiently manage your Canvas files.")
    print("=" * 50)
    
    print("\nTo get started, you'll need a Canvas API token.")
    print("To obtain a token:")
    print("1. Log in to your Canvas account.")
    print("2. Go to 'Account' > 'Settings'.")
    print("3. Scroll down to the 'Approved Integrations' section.")
    print("4. Click on '+ New Access Token'.")
    print("5. Follow the prompts to generate your token.")
    print("=" * 50)
    
    token = input("\nPlease enter your Canvas API token: ")
    return token

def is_token_valid(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('https://your-api-endpoint.com/resource', headers=headers)

    if response.status_code == 200:
        return True
    elif response.status_code == 401:
        return False
    else:
        print(f'Unexpected status code: {response.status_code}')
        return False

def main():
    global config
    global token
    config = load_config()
    global headers

    if "token" not in config:
        token = welcome()
        while not (is_token_valid(token)):
            token = input('Token is invalid or has expired. Please enter a new token: ')
        print("Token accepted!")
        config["token"] = token
            
    elif is_token_expired(config["token"]):
        token = input("The token you provided is expired. Please enter a new one: ")
        while not (is_token_valid(token)):
            token = input('Token is invalid or has expired. Please enter a new token: ')
        print("Token accepted!")
        config["token"] = token

    token = config["token"]
    headers = {"Authorization": f"Bearer {token}"}
    if "semester" not in config:
        semester = (
            "["
            + input("Enter the current semester as a 4 digit number (e.g. Semester 1 in Year 2023 ==> 2310): ")
            + "]"
        )
        config["semester"] = semester

    if "download_path" not in config:
        download_path = input("Enter the path to download files to: ").strip()
        while not os.path.exists(download_path):
            download_path = input("Path not found, enter a valid path: ").strip()
        config["download_path"] = download_path
    save_config(config)
    dic = {}
    while True:
        command = input("Enter your command: ")
        parts = command.split(" ")
        action = parts[0]
        if action == "download":
            if len(parts) == 1:  # No sub-action provided
                display_error_msg()
            else:
                sub_action = parts[1]
                if sub_action == "for":
                    course_names = parts[2:]
                    download_for_courses(course_names)
                elif sub_action == "all":
                    download_all()
                elif sub_action == "new":
                    download_new(dic)
                else:
                    display_error_msg()
        elif action == "list":
            if len(parts) == 1:  # No sub-action provided
                display_error_msg()
            else:
                sub_action = parts[1]
                if sub_action == "all":
                    list_all()
                elif sub_action == "new":
                    list_new(dic)
                else:
                    display_error_msg()
        elif action == "exit":
            print("Exiting the program.")
            break
        elif action == "help":
            display_help_msg()
        else:
            display_error_msg()

if __name__ == "__main__":
    main()
