import requests
import json

# Your Canvas API access token
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"

# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"

# Headers for API calls
headers = {'Authorization': f'Bearer {token}'}

# Function to get folders for a course or a parent folder
def get_folders(parent_type, parent_id):
    folders_url = f"{base_url}/{parent_type}/{parent_id}/folders"
    response = requests.get(folders_url, headers=headers)
    return json.loads(response.text) if response.status_code == 200 else []

# Function to get files in a folder
def get_files(folder_id):
    files_url = f"{base_url}/folders/{folder_id}/files"
    response = requests.get(files_url, headers=headers)
    return json.loads(response.text) if response.status_code == 200 else []

# Recursive function to display folders and files
def display_folders_and_files(parent_type, parent_id, indentation=0):
    folders = get_folders(parent_type, parent_id)
    for folder in folders:
        print(" " * indentation + folder['name'] + ":")
        files = get_files(folder['id'])
        for file in files:
            print(" " * (indentation + 4) + file['display_name'])
        display_folders_and_files('folders', folder['id'], indentation + 4)

# Function to get courses
def get_courses():
    courses_url = f"{base_url}/courses"
    response = requests.get(courses_url, headers=headers)
    return json.loads(response.text) if response.status_code == 200 else []

# Main function to display courses and their folders and files
def main():
    courses = get_courses()
    for course in courses:
        if 'name' in course:
            print(course['name'] + ":")
            display_folders_and_files('courses', course['id'], indentation = 4)

# Run the main function
if __name__ == "__main__":
    main()
