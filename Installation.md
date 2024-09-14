# KU Polls Installation Guide

1. Clone this repository, or download it as a zip file and extract it.
    ```
    git clone https://github.com/Jangsoodlor/ku-polls.git
    ```
1. Navigate to the project's directory
    ```
    cd ku-polls
    ```

1. Create Virtual Environment
    ```
    python -m venv env
    ```

1. Activate Virtual Environment
    - on Windows:
      ```
      .\env\Scripts\activate
      ```
    - on MacOS, Linux and other UNIX-based OS:
      ```
      ./env/bin/activate
      ```

1. Install required dependencies 
    ```
    pip install -r requirements.txt
    ```

1. Load polls and users data
    ```
    python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
    ```

1. [Run the application](README.md#running-the-application)