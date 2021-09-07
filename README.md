# cs-platform

A web application built on DRF/Django and Vue.js.
This is a take home assignment prepared for an interview.

Project board: <https://github.com/zachpang/cs-platform/projects/1>

| Feature                                                                                          | API                | SPA            |
| ------------------------------------------------------------------------------------------------ | ------------------ | -------------- |
| user registration and user authentication                                                        | :white_check_mark: | :construction: |
| create, read, update, delete of resources for users                                              | :white_check_mark: | :construction: |
| admin interface via Django Admin for administrators to manage users, user's quota, and resources | :white_check_mark: | -              |

## Run project

- Clone project - `git clone https://github.com/zachpang/cs-platform.git`
- Go to project directory - `docker-compose up`
  - Note: The node/vue app image may take up to 3 or more minutes to build due to npm packages.

## Explore API service

The API service is the DRF/Django API.

Run `docker exec -it csapi pytest` to execute all tests.

The django-admin portal is available at `localhost:8000/admin`

- make sure to run `docker exec -it csapi poetry run python src/manage.py createsuperuser` to create an admin user to login

## Explore SPA (app) service

The Vue SPA is hosted on `localhost:8080`

It is not currently wired up to any of the backend APIs as it is still a WIP. :construction:
