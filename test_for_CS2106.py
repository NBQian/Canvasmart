import requests

# Your Canvas API access token
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"

# Base URL for your Canvas instance
base_url = "https://canvas.nus.edu.sg/api/v1"

# Headers for API calls
headers = {"Authorization": f"Bearer {token}"}


# Function to get folders for a course
def get_folders(course_id):
    folders_url = f"{base_url}/courses/{course_id}/folders"
    response = requests.get(folders_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Failed to get folders for course {course_id}. Status code: {response.status_code}"
        )
        return []
