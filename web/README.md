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

On the right side of the dashboard, the user can enter the package name and package version of a package available on crates.io. After submitting this information, the package-analysis tool will analyze the package and display the reports once the analysis is complete.



# Reports

![Report Detail](images/report.png)
The report includes detailed information such as files, commands executed, domains accessed, and IP addresses involved. This data helps users understand the behavior and potential risks associated with the analyzed package.
