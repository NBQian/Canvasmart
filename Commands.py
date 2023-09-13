import requests
from Storage import *


# Function to get courses
def get_courses():
    courses_url = f"{base_url}/courses"
    response = requests.get(courses_url, headers=headers)
    if response.status_code == 200:
        return response.json()


# Function to get files for a folder
def get_files_in_folder(folder_id):
    files_url = f"{base_url}/folders/{folder_id}/files"
    response = requests.get(files_url, headers=headers)
    if response.status_code == 200:
        return response.json()


# Function to get folders for a course
def get_folders(course_id):
    folders_url = f"{base_url}/courses/{course_id}/folders"
    response = requests.get(folders_url, headers=headers)
    if response.status_code == 200:
        return response.json()


def list_new_files():
    # Get list of courses
    courses = get_courses()

    # Loop through each course
    for course in courses:
        course_id = course.get('id', 'N/A')
        course_name = course.get('name')

        # Skip courses without a name
        if not course_name:
            continue
        print(course_name)
        list_folders_files(course_id, 1)


def list_files_in_folder(folder_id, count):
    # Get and display files in this folder
    files_in_folder = get_files_in_folder(folder_id)
    spacing = "    " * count
    print(spacing + f"{'File Name':<45} {'Size':<15} {'Created At':<25}")
    print(spacing + "=" * 85)
    for file in files_in_folder:
        display_name = file.get('display_name', 'N/A')
        size = file.get('size', 'N/A')
        created_at = file.get('created_at', 'N/A')
        print(spacing + f"{display_name:<45} {size:<15} {created_at:<25}")


def list_folders_files(course_id, count):
    # Get list of folders for this course
    folders = get_folders(course_id)

    for folder in folders:
        folder_name = folder.get('name', 'N/A')
        print(f"\n  - {folder_name}:")
        files_count = folder.get('files_count')
        folders_count = folder.get('folders_count')
        folder_id = folder.get('id', 'N/A')
        if files_count == 0 and folders_count == 0:
            print("  Empty")
            continue
        elif folders_count == 0:
            list_files_in_folder(folder_id, count)
        else: # has sub-folders
            list_folders_files(course_id, count + 1)
            list_files_in_folder(folder_id, count)