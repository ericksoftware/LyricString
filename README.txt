# LyricString - Music Learning Platform

LyricString is a Django-based web application that allows users to explore, learn, and interact with music through songs, chords, lyrics, and tabs.

## Features

- User Authentication (Login, Registration, Profiles)
- Browse Songs, Artists, Genres, and Instruments
- Song Details with Lyrics, Chords, and Tabs
- Like and Save songs to your profile
- Comprehensive Admin Dashboard for content management
- Fully responsive design

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- Python (3.8 or higher)
- pip (Python package manager)
- A virtual environment tool (recommended)

## Installation & Setup

1.  **Extract the Project Zip**
    Extract the contents of the `lyricstring-final-project.zip` to a directory on your computer.

2.  **Navigate to the Project Directory**
    Open a terminal (Command Prompt, PowerShell, or Bash) and navigate to the extracted project folder.
    ```
    cd path/to/lyricstring-project
    ```

3.  **(Optional but Recommended) Create a Virtual Environment**
    This isolates the project dependencies.
    ```
    python -m venv venv
    ```
    *   **On Windows:** `.\venv\Scripts\activate`
    *   **On macOS/Linux:** `source venv/bin/activate`
    Your terminal prompt should change to show `(venv)`.

4.  **Install Required Dependencies**
    Install all necessary Python packages using the requirements.txt file.
    ```
    pip install -r requirements.txt
    ```

5.  **Run Database Migrations**
    Django needs to create its database tables.
    ```
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin Account)**
    This account will allow you to access the admin dashboard and add content.
    Follow the prompts to create a username, email, and password.
    ```
    python manage.py createsuperuser
    ```

7.  **Run the Development Server**
    Start the local web server to view the project.
    ```
    python manage.py runserver
    ```

8.  **Access the Application**
    Open your web browser and go to:
    - Main Site: `http://127.0.0.1:8000/`
    - Admin Dashboard: `http://127.0.0.1:8000/dashboard/` (Login with your superuser account)
    - Django Admin (Advanced): `http://127.0.0.1:8000/admin/`

## Loading Sample Data (Optional)

To populate the site with sample artists, genres, and instruments, run: