# Canvasmart
A self-initiated project to help NUS students manage Canvas files easily

This Python script allows users to easily download their course files from the Canvas Learning Management System. Specifically tailored for students at the National University of Singapore (NUS), the script retrieves files for a given semester and organizes them neatly in local directories.
<img width="1054" alt="image" src="https://github.com/user-attachments/assets/0c12da65-8315-4f26-b1c8-f84d2d8b995b">

## Features:

- **Authentication**: Uses Canvas API tokens to securely access course content. The API tokens are locally stored to ensure safety of your Canvas account.
  
- **Semester Filtering**: Only downloads files for a specified semester to keep things organized.
  
- **Automatic Directory Creation**: Creates directories based on course names, ensuring an organized file structure.
  
- **Duplicate Checking**: Only downloads files that don't exist locally to save bandwidth and time.
  
- **Interactive Commands**: Allows users to either list all available files or download all files.

## Prerequisites:

- Python 3
- `requests` library. Install with `pip install requests`
  
## Setup:

1. Download the script

2. Obtain your Canvas API token. You can get this from your Canvas settings.

3. Run the script: `python Canvasmart.py`

4. When prompted, enter your Canvas API token.

5. Specify the semester you want to fetch files for (e.g., `2310` for Semester 1 of 2023/2024).

6. Specify the local directory where you'd like to download the files.

7. Use the available commands (`list all`, `download all`, `exit`) to interact with the program.

## Usage:

- `list all`: Displays all available files for all courses on Canvas for the given semester.
- `list new`: Displays all available files in the Canvas that have not been downloaded to the local directory.
- `download all`: Downloads all files to the specified directory, organized by course name.
- `exit`: Exits the program.
