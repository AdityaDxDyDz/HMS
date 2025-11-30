===============================
Hospital Management App
===============================

A Flask-based web application for managing hospital operations including patients, doctors, appointments, and treatment records.

-------------------------------------------------
1. Requirements
-------------------------------------------------
Before running the project, ensure the following are installed:

- Python 3.9 or above
- pip (Python package manager)
- Virtual environment support (venv)

-------------------------------------------------
2. Opening the Project
-------------------------------------------------
Open the HMS project folder in any code editor such as VS Code.

Example structure:
HMS/
    app.py
    models.py
    routes.py
    forms.py
    helpers.py
    extensions.py
    init_db.py
    requirements.txt
    /templates
    /static

-------------------------------------------------
3. Creating the Virtual Environment
-------------------------------------------------

Windows:
    python -m venv venv
    venv\Scripts\activate

Mac/Linux:
    python3 -m venv venv
    source venv/bin/activate

After activation, (venv) should appear in the terminal prompt.

-------------------------------------------------
4. Installing Dependencies
-------------------------------------------------

Run the following inside the activated virtual environment:

    pip install -r requirements.txt

This installs Flask, Flask-Login, Flask-WTF, SQLAlchemy, and all required libraries.

-------------------------------------------------
5. Initializing the Database
-------------------------------------------------

Run the database creation script:

    python init_db.py

This will:
- Create the SQLite database file
- Create all database tables
- Automatically create the default admin user

-------------------------------------------------
6. Running the Application
-------------------------------------------------

Start the server using:

    python app.py

The terminal will display the address:

    Running on http://127.0.0.1:5000

Open this link in your browser.

-------------------------------------------------
7. Default Admin Login
-------------------------------------------------

After database initialization, a default admin account is created.

Username: admin
Password: admin123

You may modify these credentials inside init_db.py.

-------------------------------------------------
8. Application Roles and Features
-------------------------------------------------

Admin:
- Manage doctor profiles
- View, search, and manage patients
- View all appointments
- Edit doctor and patient information

Doctor:
- View upcoming appointments
- Mark appointments as Completed or Cancelled
- Enter diagnosis, prescriptions, and notes
- View patient history

Patient:
- Register and login
- View available specializations
- Book, cancel, and reschedule appointments
- View past appointments and treatment details

-------------------------------------------------
9. Project Folder Structure
-------------------------------------------------

HMS/
    app.py                - Main application entry point
    routes.py             - Blueprint routes for admin/doctor/patient
    models.py             - Database models (SQLAlchemy)
    forms.py              - WTForms for handling user inputs
    helpers.py            - Utility and helper functions
    extensions.py         - Database and LoginManager initialization
    init_db.py            - Script to create database and admin user
    /templates            - HTML templates
    /static/css           - Custom CSS files
    requirements.txt      - Required Python libraries

-------------------------------------------------
10. Troubleshooting
-------------------------------------------------

Issue: ModuleNotFoundError
Fix: Run
    pip install -r requirements.txt

Issue: Database not created
Fix: Run
    python init_db.py

Issue: CSS not loading
Fix: Ensure CSS exists at:
    /static/css/style.css

-------------------------------------------------
11. Stopping the Server
-------------------------------------------------

Press CTRL + C in the terminal to stop the application.

To exit virtual environment:
    deactivate

-------------------------------------------------
12. License
-------------------------------------------------

This project is created for educational use as part of the App Development course.
