import requests
import json
from datetime import datetime
import os
import json

CONFIG_FILE = "config.json"
config = {}


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"


def is_token_expired(token):
    h = {"Authorization": f"Bearer {token}"}
    test_url = f"{base_url}/courses"
    response = requests.get(test_url, headers=h)

    # Checking for unauthorized or forbidden status codes
    if response.status_code == 401 or response.status_code == 403:
        # Optionally, check for specific message in response to confirm token issue
        if (
            "token is expired" in response.text
        ):  # This message may vary, check Canvas API documentation
            return True
        return False
    elif response.status_code == 200:
        return False
    else:
        print(f"Unexpected response code: {response.status_code}")
        return False


# Function to get paginated data
def get_paginated_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(json.loads(response.text))
            # Check if there is a next page
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


# Function to get folders for a course or a parent folder
def get_folders(parent_type, parent_id):
    folders_url = f"{base_url}/{parent_type}/{parent_id}/folders"
    return get_paginated_data(folders_url)


# Function to get files in a folder
def get_files(folder_id):
    files_url = f"{base_url}/folders/{folder_id}/files"
    return get_paginated_data(files_url)


# Function to get courses
def get_courses():
    courses_url = f"{base_url}/courses"
    all_courses = get_paginated_data(courses_url)

    filtered_courses = []
    for course in all_courses:
        if "created_at" in course:
            if course["name"].endswith(config["semester"]):
                filtered_courses.append(course)

    return filtered_courses


# Function to get modules for a course
def get_modules(course_id):
    modules_url = f"{base_url}/courses/{course_id}/modules"
    return get_paginated_data(modules_url)


# Function to get items in a module
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
    # First, create any sub-folders
    subfolders = get_folders("folders", folder_id)
    for subfolder in subfolders:
        if subfolder["name"] == "unfiled":  # Skip the 'unfiled' folder
            continue
        subfolder_path = os.path.join(destination_path, subfolder["name"])
        os.makedirs(subfolder_path, exist_ok=True)
        download_files_in_folder(subfolder["id"], subfolder_path)

    # Then, download the files in the current folder
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
            if folder["name"] != "unfiled":
                download_files_in_folder(folder["id"], course_path)
    else:
        # If no 'files' section, download from the 'modules' section
        download_files_by_modules(course_id, course_path)


def download_all():
    # Starting with the path provided by the user
    root_folder = config["download_path"]

    # Check if the directory exists, if not then create it
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)

    courses = get_courses()
    for course in courses:
        if "name" in course and course["name"][:6] == "CS2105":
            course_path = os.path.join(root_folder, course["name"][:6])

            # Check if the course directory exists, if not then create it
            if not os.path.exists(course_path):
                os.makedirs(course_path)

            download_files_for_course(course["id"], course_path)


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
        if "name" in course and course["name"].endswith("[2310]"):
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


def main():
    global config
    global token
    config = load_config()
    # Headers for API calls
    global headers

    if "token" not in config or is_token_expired(config["token"]):
        print("Please provide your Canvas API token.")
        print("Instructions: [provide instructions on how to get the token here]")
        token = input("Enter token: ")
        config["token"] = token
        if is_token_expired(token):
            print("The token you provided is invalid or expired. Please get a new one.")
            return
        else:
            print("Token accepted!")
    token = config["token"]
    headers = {"Authorization": f"Bearer {token}"}
    if "semester" not in config:
        semester = (
            "["
            + input("Enter the current semester as a 4 digit number (e.g. 2310): ")
            + "]"
        )
        config["semester"] = semester

    if "download_path" not in config:
        download_path = input("Enter the path to download files to: ")
        config["download_path"] = download_path
    save_config(config)

    while True:
        # Wait for user input
        user_input = input("Enter your command: ")

        # Handle the possible commands
        if user_input == "list all":
            list_all()
        elif user_input == "download all":
            download_all()
        elif user_input == "exit":
            print("Exiting the program.")
            break
        else:
            print("Instruction not recognized. Please enter a valid command.")


if __name__ == "__main__":
    main()
