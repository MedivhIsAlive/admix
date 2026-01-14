### Introduction

This is a django drf project with logic for generating periodic reports based on data from models


### Set-up

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

2. Migrations and test
   `python3 manage.py makemigrations`
   `python3 manage.py migrate`
   `python3 manage.py test`
