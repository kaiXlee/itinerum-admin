# itinerum-admin

[![Python Version](https://img.shields.io/badge/Python-2.7-blue.svg?style=flat-square)]()


This repository contains the Flask application for the Itinerum admin portal and accompanying Dockerfile. It is a survey management panel for the [Itinerum travel survey platform](https://itinerum.ca/).

### Development Guide

The most important guideline is the `master` branch should always contain a working version of the application with appropriate unit tests. New features should be developed in a branch of the master named  as `feature-name-action`, for example: `survey-wizard-upsert-dropdown-options`.

#### Contributing

- Fork this repository to your own account
- Edit the project to include your new contributions
- After all tests pass, create a pull request to this project
- Accepted changes will be merged when code is reviewed

## Getting Started

### Base Requirements
- Python 3.6
- PostgreSQL 10

### Cloning the Project

It is recommended to create a single shared virtualenv for the Itinerum APIs with [virtualenv-wrapper](http://virtualenvwrapper.readthedocs.io), which makes virtualenvs friendlier to user. In the examples that follow, a virtualenv name of `admin` will be used.

Create a local `itinerum` project directory, make a new virtualenv for the `itinerum-admin` repo and install the dependencies:

```bash
$ cd <your-local-itinerum-project>
$ git clone git@github.com:TRIP-Lab/itinerum-admin.git
$ cd itinerum-admin
$ mkvirtualenv admin
$ (admin) pip install -r requirements.txt
```

### Database

##### Setup

First, create the development PostgreSQL database named `itinerum_dev`. The database migrations are perfomed manually using the the incremented .sql files within the migrations directory. Connect to the development database with `psql` as follows:


```bash
$ psql itinerum_dev
# \i migrations\up\1-itinerum-database.sql
  ...
# \i migrations\up\n-itinerum-database.sql
```

For any modifications to the database, create an .sql `up` and `down` migration within the `./migrations` directory and apply like above.

### Development

The application expects configuration values to be set by environment variables. For the testing environment, the best way is to set these as normal environment variables either through Windows or in ~/.bash_profile (usually) on a Unix-based platform. Expected variables can found within `conf/sample` and can be set by [sourcing](https://en.wikipedia.org/wiki/Source_(command)) this file.

Launch the Flask development server with:

````Bash
(admin) $ python manage.py runserver
````

The debug server will run default to port 9002 and will be accessible at: `http://localhost:9002`. Before your changes are committed, the following Docker build should be tested and passing as well.



##### Docker

A provided Docker build file allows running the project repository in an encapsulated environment without having to worry about conflcts of dependencies on your local host. 

For running `ititinerum-admin` with Docker, first build the image with:

```bash
$ docker build -t itinerum-admin:latest .
```



Add a local _environment variables_ configuration file (e.g., `./conf/dev_env`) to run the compiled Docker with:

```bash
$ docker run -d -p 9002:9002 --env-file=conf/dev_env --name=itinerum-admin itinerum-admin:latest
```

The portal can then be reached at: `http://<docker-machine-address>:9002/admin`

*Note*: It can be tricky to get the Docker version of the application communicate to the PostgreSQL database on the host system. Be sure that the `dev_env` file reflects the LAN address of the Host system and an existing database. It is useful to watch for events in the `postgresql.log` file to diagnose issues here.
