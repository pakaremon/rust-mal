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
![home page](images/homepage.png)
The homepage shows featutes of projects and contact informations.

![Dashboard Screenshot](images/dashboard.png)

On the right side of the dashboard, the user can enter the package name and package version of a package available on crates.io. After submitting this information, the package-analysis tool will analyze the package and display the reports once the analysis is complete.



# Reports

![Report Detail](images/report.png)
The report includes detailed information such as files, commands executed, domains accessed, and IP addresses involved. This data helps users understand the behavior and potential risks associated with the analyzed package.

# Run on azure
```bash
 cd rust-mal/web/package-analysis-web
#  Create virtual environment
python -m venv .env
# Active virtual environment
source .env/bin/activate
# Install libraries
pip install -r requirements.txt
```
Create database

```bash
python manage.py makemigrations
python manage.py migrates
```

Using unicorn to run
```bash
gunicorn --bind 0.0.0.0:8000 package_analysis_apk_web.wsgi:application
```

Run on web server on port 80

```bash
sudo env "PATH=$PATH" python manage.py runserver 0.0.0.0:80
```
OR
```bash
sudo $(which python) manage.py runserver 0.0.0.0:80
```

# Install tools
Install ['Docker in Ubuntu'](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04)

### Install OSS-Find-Squat & OSS-detect-backdoor

1. Install [`Oss-gadget v0.1.422`](https://github.com/microsoft/OSSGadget/releases/download/v0.1.422/OSSGadget_linux_0.1.422.tar.gz).
2. [`Extract and build docker`](https://github.com/microsoft/OSSGadget/wiki/Docker-Image)



# TODO: Automation
https://www.geeksforgeeks.org/how-to-setup-cron-jobs-in-ubuntu/

https://appliku.com/post/setting-nginx-django-project/

