# Job Portal Project

A Django-based job portal web application where employers can post jobs, candidates can apply with resumes, and admins can monitor platform activity through a dashboard.

## Overview

This repository contains two Django projects:

- `jobportal/` - the main job portal application
- `login/` - a smaller authentication practice project

If you are running the main project for GitHub/demo purposes, use the `jobportal/` folder.

## Features

- User signup and login
- Role-based accounts for employers and candidates
- Employer dashboard for posting and managing jobs
- Candidate dashboard for viewing submitted applications
- Job listing page with keyword and location search
- Resume upload while applying for jobs
- Admin dashboard with user, job, and application statistics
- Built with Django and SQLite for simple local setup

## Tech Stack

- Python
- Django 5
- SQLite
- HTML templates

## Project Structure

```text
FinalProject/
├── jobportal/              # Main Django job portal project
│   ├── job/                # Main application
│   ├── jobportal/          # Project settings and URLs
│   ├── media/              # Uploaded resumes
│   ├── db.sqlite3
│   └── manage.py
├── login/                  # Separate basic login/signup Django project
└── README.md
```

## Main Modules

### `jobportal/`

The primary project includes:

- `UserProfile` model for storing user roles
- `Job` model for posted jobs
- `Application` model for candidate applications and resume uploads
- Employer, candidate, and admin dashboards

### `login/`

A basic standalone authentication demo with:

- Signup
- Login
- Logout
- Protected home route

## How to Run the Main Project

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FinalProject
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Move into the main project folder

```bash
cd jobportal
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Main Routes

- `/` - home page with job listings
- `/signup/` - user registration
- `/login/` - user login
- `/logout/` - user logout
- `/dashboard/` - employer or candidate dashboard
- `/post-job/` - create a job post
- `/apply/<id>/` - apply for a job
- `/admin/` - Django admin panel
- `/admin-dashboard/` - custom admin dashboard

## Default Roles

- `Employer` can post jobs and view applications count on their dashboard
- `Candidate` can browse jobs and upload resumes while applying
- `Admin` can access platform-level statistics and recent activity

## Database

The project currently uses SQLite:

- `jobportal/db.sqlite3` for the main job portal
- `login/db.sqlite3` for the standalone login project

This makes local development easy, but for deployment you should switch to a production-ready database like PostgreSQL.

## Notes

- Uploaded resumes are stored in `jobportal/media/resumes/`
- The repository currently includes local development databases
- `SECRET_KEY` and `DEBUG=True` are set for development only and should be changed before deployment

## Future Improvements

- Add a `requirements.txt`
- Add profile details such as company name, skills, and contact info
- Add job editing and deletion
- Add employer view for submitted applications
- Add email notifications
- Improve validation and file upload restrictions
- Deploy with PostgreSQL and cloud media storage

## Author

Created as a Django full-stack mini project for a job portal workflow.
