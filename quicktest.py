import requests
import json
from datetime import datetime
import pytz
import os

# Your Canvas API access token
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"

# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"

# Headers for API calls
headers = {"Authorization": f"Bearer {token}"}


# Function to get paginated data
# Function to get paginated data
def get_paginated_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            all_data.extend(data)

            # Check for pagination
            link_header = response.headers.get("Link", None)
            if link_header:
                links = link_header.split(",")
                next_link = None
                for link in links:
                    if 'rel="next"' in link:
                        next_link = link.split(";")[0].strip("<>")
                        break
                url = next_link
            else:
                url = None
        else:
            print(f"Failed to get data. Status code: {response.status_code}")
            break
    return all_data


# Function to get courses
def get_courses():
    courses_url = f"{base_url}/courses"
    all_courses = get_paginated_data(courses_url)

    # Create a datetime object for June 1, 2023, and make it timezone-aware
    cutoff_date = datetime.strptime("2023-06-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    cutoff_date = pytz.utc.localize(cutoff_date)  # Assuming UTC timezone

    filtered_courses = []
    for course in all_courses:
        if "created_at" in course:
            course_created_at = datetime.fromisoformat(course["created_at"])
            if course_created_at <= cutoff_date:
                filtered_courses.append(course)

    return filtered_courses


# Function to get files for a course
def get_course_files(course_id):
    files_url = f"{base_url}/courses/{course_id}/files"
    return get_paginated_data(files_url)


def get_course_folders(course_id):
    folders_url = f"{base_url}/courses/{course_id}/folders"
    return get_paginated_data(folders_url)


def get_course_folders_through_parentID(id):
    gcftp_url = f"{base_url}/courses/{id}/folders"
    return get_paginated_data(gcftp_url)


folders = get_course_folders_through_parentID(45706)
files = get_course_files(45706)
# folders = get_course_folders(45706)

for folder in folders:
    print(
        folder["name"],
        folder["files_count"],
        folder["folders_count"],
        folder["hidden"],
        folder["hidden_for_user"],
    )
folder_path = f"{base_url}/courses/45706"
items = os.listdir(folder_path)
print(items)

# for file in files:
#     print(file["filename"])
# courses = get_courses()
# for course in courses:
#     if "name" in course:
#         print(course["name"], course["id"])
# #     else:
# #         continue
# #     files = get_course_files(course["id"])
# #     for file in files:
# #         print(file["filename"])
# #     print("\n\n")
# print("nima")
