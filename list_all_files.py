import requests
import json
from datetime import datetime
import os

# Your Canvas API access token
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"

# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"

# Headers for API calls
headers = {"Authorization": f"Bearer {token}"}


# Recursive function to display folders and files
def display_folders_and_files(parent_type, parent_id, indentation=0):
    folders = get_folders(parent_type, parent_id)
    if parent_type == "courses":
        main_folder_id = 0
        main_folder = None
        for folder in folders:
            if folder["name"] == "course files":
                main_folder_id = folder["id"]
                main_folder = folder
                break
        first_layer_folders = [
            folder for folder in folders if folder["parent_folder_id"] == main_folder_id
        ]
        first_layer_folders.append(main_folder)
        folders = first_layer_folders

    for folder in folders:
        if parent_type == "folders" and folder["parent_folder_id"] != parent_id:
            continue  # Skip if this is not a direct child of the current folder
        if folder["files_count"] == 0 and folder["folders_count"] == 0:
            continue

        # Special case for "course files" folder
        if folder["name"] == "course files":
            special_indentation = indentation
        else:
            folder_name = folder["name"]
            dash_line = "\-" * (len(folder_name) // 2)
            print(" " * indentation + folder_name)
            print(" " * indentation + f" {dash_line}")
            special_indentation = indentation + 4

        files = get_files(folder["id"])
        for file in files:
            print(" " * special_indentation + file["display_name"])
        if folder["name"] != "course files":
            display_folders_and_files("folders", folder["id"], special_indentation)


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
            course_sem = course["name"][-6:]
            if course_sem == "[2310]":
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


# Function to get files for a course
def get_course_files(course_id):
    files_url = f"{base_url}/courses/{course_id}/files"
    return get_paginated_data(files_url)


def download_file(url, destination_path):
    with requests.get(url, stream=True, headers=headers) as response:
        with open(destination_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)


def download_files_in_folder(folder_id, destination_path):
    # First, create any sub-folders
    subfolders = get_folders("folders", folder_id)
    for subfolder in subfolders:
        subfolder_path = os.path.join(destination_path, subfolder["name"])
        os.makedirs(subfolder_path, exist_ok=True)
        download_files_in_folder(subfolder["id"], subfolder_path)

    # Then, download the files in the current folder
    files = get_files(folder_id)
    for file in files:
        download_file(file["url"], os.path.join(destination_path, file["display_name"]))


def download_files_for_course(course_id, course_path):
    folders = get_folders("courses", course_id)
    for folder in folders:
        if folder["name"] == "course files":
            download_files_in_folder(folder["id"], course_path)
            break


def download_all_folders_and_files():
    # Starting with the 'my files' folder in the home directory
    root_folder = os.path.join(os.path.expanduser("~"), "my files")
    os.makedirs(root_folder, exist_ok=True)

    courses = get_courses()
    for course in courses:
        if (
            "name" in course
            and course["name"] == "CS2106 Introduction to Operating Systems [2310]"
        ):
            course_path = os.path.join(root_folder, course["name"])
            os.makedirs(course_path, exist_ok=True)
            download_files_for_course(course["id"], course_path)


# Main function to display courses and their folders and files
def list_all_files():
    courses = get_courses()
    for course in courses:
        if "name" in course:
            course_name = course["name"]
            equal_line = "=" * len(course_name)
            print(f"\n{equal_line}\n{course_name}\n{equal_line}")
            display_folders_and_files("courses", course["id"], indentation=4)
            # Check if there are files in the 'files' section
            course_files = get_course_files(course["id"])
            if course_files:
                display_folders_and_files("courses", course["id"], indentation=4)
            else:
                print("    No files found in 'files' path. Checking 'Modules'...")

                # Fetch and display module items
                modules = get_modules(course["id"])
                for module in modules:
                    print("    " + module["name"] + ":")
                    items = get_module_items(course["id"], module["id"])
                    for item in items:
                        if item["type"] == "File":
                            print("        " + item["title"])
