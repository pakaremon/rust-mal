# Web Interface for Package Analysis

## Installation

### Requirements
- Docker
- Django
- requests
- WSL (Windows Subsystem for Linux) on Windows or Linux

## Usage

```bash
cd rust-mal/web/package-analysis-web
```

Create Database to store informations:

```bash
    python manage.py makemigrations
```

Then apply these migrations to our database, run this command:

```bash
    python manage.py migrate
```

Run the server by using this command. 
```bash
python manage.py runserver
```

Access the web interface at [127.0.0.1:8000/package-analysis](http://127.0.0.1:8000/package-analysis)

## Demo

![Dashboard Screenshot](images/dashboard.png)

Tech Stack: Django

This dashboard shows a web interface built using the Django framework.



# Reports

![Report Detail](images/report.png)


