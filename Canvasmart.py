# import requests

# token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"
# url_course = 'https://canvas.nus.edu.sg/api/v1/courses'
# headers = {'Authorization': f'Bearer {token}'}

# # course_id = 44844

# # url_file = f"https://canvas.nus.edu.sg/api/v1/courses/{course_id}/files"



# # response = requests.get(url_file, headers=headers)

# # if response.status_code == 200:
# #     file_object = response.json()
# #     print(f"{'File Name':<50} {'Size':<20} {'Created At':<30}")
# #     print("="*100)

# #     for file in file_object:
# #         display_name = file.get('display_name', 'N/A')
# #         size = file.get('size', 'N/A')
# #         created_at = file.get('created_at', 'N/A')
# #         print(f"{display_name:<50} {size:<20} {created_at:<30}")
# response = requests.get(url_course, headers=headers)
# if response.status_code == 200:
#     courses_object = response.json()
#     for course in courses_object:
#         course_name = course.get('name')
#         if course_name:
#             print(course_name)
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
        # print(f"Failed to get files for folder {folder_id}. Status code: {response.status_code}")
        # return []
        return

# Function to get folders for a course
def get_folders(course_id):
    folders_url = f"{base_url}/courses/{course_id}/folders"
    response = requests.get(folders_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get folders for course {course_id}. Status code: {response.status_code}")
        return []

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

    # Get list of folders for this course
    folders = get_folders(course_id)

    for folder in folders:
        folder_id = folder.get('id', 'N/A')
        folder_name = folder.get('name', 'N/A')
        print(f"\n  - {folder_name}")

        # Get and display files in this folder
        files_in_folder = get_files_in_folder(folder_id)
        if not files_in_folder:
            continue
        print(f"    {'File Name':<45} {'Size':<15} {'Created At':<25}")
        print("    " + "="*85)
        for file in files_in_folder:
            display_name = file.get('display_name', 'N/A')
            size = file.get('size', 'N/A')
            created_at = file.get('created_at', 'N/A')
            print(f"    {display_name:<45} {size:<15} {created_at:<25}")
    print("\n")






