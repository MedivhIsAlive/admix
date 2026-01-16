### Introduction

This is a django drf project with logic for generating periodic reports based on data from models

### Prerequisites
Docker and Docker Compose (if using Docker)
Python 3.10+ (if running locally)
PostgreSQL (if running locally)

### Set-up

.env file needs to be inside the project directory

POSTGRES_DB=*
POSTGRES_USER=*
POSTGRES_PASSWORD=*

SECRET_KEY=*
DEBUG=True
DATABASE_URL=postgres://app_user:secret@db:*/app_db


If you want to go docker way, then just do

1. `docker compose up -d --build`
2. `docker compose exec web python manage.py makemigrations`
3. `docker compose exec web python manage.py migrate`
4. `docker compose exec web python manage.py test`

If you want to set it up locally, then

1. Create the environment and install all dependencies:
   `python3 -m venv ./venv`
   `source ./venv/bin/activate`
   `python3 -m pip install -r requirements.txt`
2. Migrations and test(assuming your db is already confugired)
   `python3 manage.py makemigrations`
   `python3 manage.py migrate`
   `python3 manage.py test`
3. If you dont wanna hardcode the settings, you can use sm like load_dotenv to load the .env file

<img width="1621" height="498" alt="image" src="https://github.com/user-attachments/assets/04d598b3-3060-4671-8c68-642a3f64f8e3" />
