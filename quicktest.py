import requests

# Your Canvas API access token
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"

# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"

# Headers for API calls
headers = {'Authorization': f'Bearer {token}'}

# Function to get courses
def get_courses():
    courses_url = f"{base_url}/courses"
    response = requests.get(courses_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get courses. Status code: {response.status_code}")
        return []

# Function to get files for a folder
def get_files_in_folder(folder_id):
    files_url = f"{base_url}/folders/{folder_id}/files"
    response = requests.get(files_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get files for folder {folder_id}. Status code: {response.status_code}")
        return []

# Function to get folders for a course
def get_folders(course_id):
    folders_url = f"{base_url}/courses/{course_id}/folders"
    response = requests.get(folders_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get folders for course {course_id}. Status code: {response.status_code}")
        return []

def get_files_in_courses(course_id):
    files_url = f"{base_url}/courses/{course_id}/files"
    response = requests.get(files_url, headers)
    files = response.json()
    for file in response:
        print(file.get('filename'))

# Get list of courses
courses = get_courses()

# Loop through each course
for course in courses:
    course_id = course.get('id', 'N/A')
    course_name = course.get('name', 'N/A')
    get_files_in_courses(course_id)
    # # Skip courses without a name
    # if not course_name:
    #     continue

    # print(f"Course ID: {course_id}, Course Name: {course_name}")

    # # Get list of folders for this course
    # folders = get_folders(course_id)
    # print("Folders:")
    # for folder in folders:
    #     folder_id = folder.get('id', 'N/A')
    #     folder_name = folder.get('name', 'N/A')
    #     print(f"  - {folder_name}")

    #     print(f"\n{folder.get('files_count')}")

    #     # Get and display files in this folder
    #     files_in_folder = get_files_in_folder(folder_id)
    #     print(f"    {'File Name':<45} {'Size':<15} {'Created At':<25}")
    #     print("    " + "="*85)
    #     for file in files_in_folder:
    #         display_name = file.get('display_name', 'N/A')
    #         size = file.get('size', 'N/A')
    #         created_at = file.get('created_at', 'N/A')
    #         print(f"    {display_name:<45} {size:<15} {created_at:<25}")
    print("\n")
