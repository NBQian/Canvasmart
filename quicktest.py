import requests
import json

# Configuration
token = "21450~ib3PcTIWpRbqQW8FipYOIjYYWtdaxtPWj0YODMYaPzmMilt2kmZCx5OE4Gpe6Gxe"
base_url = "https://canvas.nus.edu.sg/api/v1"
headers = {"Authorization": f"Bearer {token}"}


def get_paginated_data(url):
    all_data = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            all_data.extend(response.json())
            # Check if there's a next page
            link_header = response.headers.get("Link", None)
            next_links = [
                l.split(";")[0][1:-1]
                for l in link_header.split(",")
                if 'rel="next"' in l
            ]
            url = next_links[0] if next_links else None
        else:
            break
    return all_data


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


def main():
    courses = get_paginated_data(f"{base_url}/courses")
    for course in courses:
        if "name" in course and course["name"].endswith("[2310]"):
            print("=" * len(course["name"]))
            print(course["name"])
            print("=" * len(course["name"]))

            course_files = get_paginated_data(
                f"{base_url}/courses/{course['id']}/files"
            )
            if course_files:
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


if __name__ == "__main__":
    main()
