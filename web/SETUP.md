# Security Setup Guide - Least Privilege Principles

This guide provides step-by-step instructions for setting up the Packamal web application with security best practices and least privilege principles.

## Table of Contents

1. [System User Creation](#1-system-user-creation)
2. [Project Setup](#2-project-setup)
3. [PostgreSQL Configuration](#3-postgresql-security-configuration)
4. [File System Permissions](#4-file-system-permissions)
5. [Docker Security](#5-docker-security)
6. [Application Security Settings](#6-application-security-settings)
7. [Network Security](#7-network-security)
8. [Firewall Configuration](#8-firewall-configuration)
9. [SSL/TLS Configuration](#9-ssltls-configuration)
10. [Monitoring and Logging](#10-monitoring-and-logging)

---

## 1. System User Creation

### Create a Dedicated Application User

Create a non-privileged user specifically for running the application:

```bash
# Create a system user without home directory and without shell access
sudo useradd -r -s /bin/bash -m -d /opt/packamal packamal

# Set a strong password (or use SSH keys instead)
sudo passwd packamal

# Verify user creation
id packamal
```

**Security Notes:**
- `-r`: Creates a system user (UID < 1000)
- `-s /bin/bash`: Allows shell access (can be changed to `/bin/false` for no shell)
- `-m`: Creates home directory
- `-d /opt/packamal`: Sets custom home directory

### Create Application Directory Structure

```bash
# Create application directories with proper ownership
sudo mkdir -p /opt/packamal/{app,logs,media,staticfiles,venv}
sudo chown -R packamal:packamal /opt/packamal
sudo chmod 750 /opt/packamal
```

### Configure SSH Access (Optional but Recommended)

If you need SSH access, configure it securely:

```bash
# Create .ssh directory
sudo mkdir -p /opt/packamal/.ssh
sudo chmod 700 /opt/packamal/.ssh

# Copy your public key (replace with your actual key)
sudo nano /opt/packamal/.ssh/authorized_keys
# Paste your public SSH key here

# Set proper permissions
sudo chown -R packamal:packamal /opt/packamal/.ssh
sudo chmod 600 /opt/packamal/.ssh/authorized_keys
```

---

## 2. Project Setup

### Clone the Project

Switch to the application user and clone the repository:

```bash
# Switch to the application user
sudo su - packamal

# Navigate to application directory
cd /opt/packamal/app

# Clone the repository
git clone https://github.com/pakaremon/rust-mal.git .

# Verify clone
ls -la
```

### Set Up Python Virtual Environment

```bash
# Create virtual environment in dedicated directory
python3 -m venv /opt/packamal/venv

# Activate virtual environment
source /opt/packamal/venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
cd /opt/packamal/app/web/packamal
pip install -r requirements.txt
```

### Configure Environment Variables

Create a secure `.env` file:

```bash
# Create .env file with restricted permissions
cd /opt/packamal/app/web/packamal
nano .env
```

Add the following content (generate secure values):

```bash
# Django Settings
SECRET_KEY=SECRET_KEY=u2r650z&35a#^=4_l5^(%ycn--=+b_m+7y9q@xx3*1vq-6_tqi
DEBUG=False
ALLOWED_HOSTS=152.42.180.203,127.0.0.1,packguard.dev,www.packguard.dev,157.230.194.230,localhost,152.42.180.203

# Database Settings
DB_NAME=packamal
DB_USER=packamal_db
DB_PASSWORD=rock-beryl-say-devices
DB_HOST=localhost
DB_PORT=5432

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# Redis Settings (
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# analysis image

ANALYSIS_IMAGE=docker.io/pakaremon/analysis
```

**Generate Secret Key:**
```bash
source /opt/packamal/venv/bin/activate
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**Set File Permissions:**
```bash
# Restrict .env file permissions
chmod 600 /opt/packamal/app/web/packamal/.env
chown packamal:packamal /opt/packamal/app/web/packamal/.env
```

---

## 3. PostgreSQL Security Configuration

### Create Database User with Least Privilege

```bash
# Switch to postgres user
sudo -u postgres psql
```

Run the following SQL commands:

```sql
-- Create database
CREATE DATABASE packamal;

-- Create user with strong password (replace with your password)
CREATE USER packamal_db WITH PASSWORD 'your-strong-password-here';

-- Configure user settings
ALTER ROLE packamal_db SET client_encoding TO 'utf8';
ALTER ROLE packamal_db SET default_transaction_isolation TO 'read committed';
ALTER ROLE packamal_db SET timezone TO 'UTC';

-- Grant ONLY necessary privileges (not superuser)
GRANT CONNECT ON DATABASE packamal TO packamal_db;
GRANT USAGE ON SCHEMA public TO packamal_db;

-- Grant privileges on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO packamal_db;

-- Grant privileges on sequences (for auto-increment fields)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO packamal_db;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO packamal_db;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO packamal_db;

--Fulll privileges ==> Caustion
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO packamal_db;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO packamal_db;

-- Revoke public schema access from public role
REVOKE ALL ON SCHEMA public FROM public;

-- Exit PostgreSQL
\q
```

### Secure PostgreSQL Configuration

Edit PostgreSQL configuration:

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Set the following security parameters:

```conf
# Connection settings
listen_addresses = 'localhost'  # Only listen on localhost

# Security settings
ssl = on
password_encryption = scram-sha-256

# Logging
log_connections = on
log_disconnections = on
log_duration = on
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

Edit `pg_hba.conf`:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Ensure local connections use password authentication:

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

---

## 4. File System Permissions

### Set Proper Directory Permissions

```bash
# Application files - readable and executable by owner only
sudo chown -R packamal:packamal /opt/packamal/app
sudo find /opt/packamal/app -type f -exec chmod 640 {} \;
sudo find /opt/packamal/app -type d -exec chmod 750 {} \;

# Make manage.py executable
sudo chmod 750 /opt/packamal/app/web/packamal/manage.py

# Virtual environment - readable by owner only
sudo chown -R packamal:packamal /opt/packamal/venv
sudo chmod -R 750 /opt/packamal/venv

# Logs directory - writable by owner only
sudo chown -R packamal:packamal /opt/packamal/logs
sudo chmod 750 /opt/packamal/logs

# Media and static files - readable by web server, writable by app user
sudo chown -R packamal:www-data /opt/packamal/media
sudo chown -R packamal:www-data /opt/packamal/staticfiles
sudo chmod 750 /opt/packamal/media
sudo chmod 750 /opt/packamal/staticfiles
sudo find /opt/packamal/media -type f -exec chmod 640 {} \;
sudo find /opt/packamal/staticfiles -type f -exec chmod 640 {} \;
```

### Protect Sensitive Files

```bash
# Ensure .env is protected
sudo chmod 600 /opt/packamal/app/web/packamal/.env
sudo chown packamal:packamal /opt/packamal/app/web/packamal/.env

# Protect database credentials
sudo chmod 600 /opt/packamal/app/web/packamal/.env

# Ensure .git directory is protected
sudo chmod -R 750 /opt/packamal/app/.git
```

---

## 5. Docker Security

### Install Docker Securely

```bash
# Install prerequisites
sudo apt update
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add packamal user to docker group 
sudo usermod -aG docker packamal
```

**Security Warning:** Adding users to the docker group grants root-equivalent privileges. Consider using rootless Docker or restricting Docker socket access.

### Configure Docker Daemon Security

Edit Docker daemon configuration:

```bash
sudo nano /etc/docker/daemon.json
```

Add security settings:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userns-remap": "default",
  "no-new-privileges": true,
  "icc": false,
  "userland-proxy": false
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

### Pull Docker Images Securely

```bash
# Switch to packamal user
sudo su - packamal

# Pull required images

docker pull pakaremon/analysis:latest

# Verify image integrity
docker images
```

---

## 6. Application Security Settings

### Update Django Settings for Production

Edit the Django settings file:

```bash
sudo nano /opt/packamal/app/web/packamal/packamal/settings.py
```

Add or update security settings:

```python
# Security Settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Password Security
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/opt/packamal/logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Run Django Migrations

```bash
# Switch to packamal user
sudo su - packamal
source /opt/packamal/venv/bin/activate
cd /opt/packamal/app/web/packamal

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### Create Superuser Securely

```bash
# Create superuser (interactive)
python manage.py createsuperuser

# Or create non-interactively (for automation)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'strong-password-here')
EOF
```

---

## 7. Network Security

### Configure Application to Listen on Localhost Only

For development or when behind a reverse proxy:

```bash
# Run Django on localhost only
python manage.py runserver 127.0.0.1:8000
```

### Set Up Reverse Proxy with Nginx

Install Nginx:

```bash
sudo apt install -y nginx
```

Create Nginx configuration:

```bash
sudo nano  /etc/nginx/sites-available/packamal 
```

Add configuration:

```nginx
server {

        root /var/www/packguard/html;
        index index.html index.htm index.nginx-debian.html;

        server_name packguard.dev www.packguard.dev;

       # location / {
       #         try_files $uri $uri/ =404;
       # }
    location = /favicon.ico { access_log off; log_not_found off; }
    
    # Serve static files
    location /static/ {
            alias /var/www/packamal/static/;
    }
    
    
    # Proxy all other requests to Django/Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }

    listen [::]:443 ssl ipv6only=on; # managed by Certbot
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/packguard.dev/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/packguard.dev/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot


}

server {
    if ($host = www.packguard.dev) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    if ($host = packguard.dev) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


        listen 80;
        listen [::]:80;

        server_name packguard.dev www.packguard.dev;
    return 404; # managed by Certbot

}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/packamal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 8. Firewall Configuration

### Configure UFW 

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (important - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming connections by default
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### Configure iptables (Alternative)

```bash
# Flush existing rules
sudo iptables -F
sudo iptables -X

# Set default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Save rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## 9. SSL/TLS Configuration

### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d packguard.dev -d www.packguard.dev

# Test automatic renewal
sudo certbot renew --dry-run
```

### Set Up Auto-Renewal

Certbot creates a systemd timer automatically. Verify it's enabled:

```bash
sudo systemctl status certbot.timer
```

---

## 10. Monitoring and Logging

### Set Up Log Rotation

Create logrotate configuration:

```bash
sudo nano /etc/logrotate.d/packamal
```

Add:

```
/opt/packamal/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 packamal packamal
    sharedscripts
    postrotate
        systemctl reload gunicorn || true
    endscript
}
```

### Set up Systemd service for Celery

```bash
ot@edu-vps-sgp1:/etc/systemd/system# cat /etc/systemd/system/celery.service 
[Unit]
Description=Celery Worker for Packamal
After=network.target redis-server.service
# If you use RabbitMQ, change redis-server.service to rabbitmq-server.service

[Service]
Type=forking
User=packamal
Group=packamal
WorkingDirectory=/opt/packamal/app/web/packamal
#EnvironmentFile=/etc/conf.d/celery
ExecStart=/opt/packamal/venv/bin/celery -A packamal worker --loglevel=INFO --concurrency=1 --detach --pidfile=/run/celery/worker.pid
#ExecStop=/opt/packamal/venv/bin/celery control shutdown
#PIDFile=/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

### Set Up Systemd Service for Gunicorn

Create systemd service file:



```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add:

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=packamal
Group=www-data
WorkingDirectory=/opt/packamal/app/web/packamal
ExecStart=/opt/packamal/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          packamal.wsgi:application

[Install]
WantedBy=multi-user.target
```


```bash
sudo nano /etc/systemd/system/gunicorn.socket 
```

Add:

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

---

## Security Checklist

- [ ] Dedicated non-privileged user created
- [ ] Application files owned by application user
- [ ] File permissions set correctly (640 for files, 750 for directories)
- [ ] `.env` file has 600 permissions
- [ ] Database user has least privilege (not superuser)
- [ ] PostgreSQL configured to listen on localhost only
- [ ] Strong passwords set for all accounts
- [ ] Django `DEBUG=False` in production
- [ ] SSL/TLS certificates installed
- [ ] Firewall configured and enabled
- [ ] Security headers configured in Nginx
- [ ] Logging configured and monitored
- [ ] Regular backups scheduled
- [ ] System updates automated
- [ ] Docker configured with security options
- [ ] SSH access secured (key-based authentication)

---


## Troubleshooting

### Permission Denied Errors

```bash
# Check file ownership
ls -la /opt/packamal

# Fix ownership if needed
sudo chown -R packamal:packamal /opt/packamal
```

### Database Connection Issues

```bash
# Test database connection
sudo -u packamal psql -h localhost -U packamal_db -d packamal

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Service Not Starting

```bash
# Check service status
sudo systemctl status gunicorn

# Check logs
sudo journalctl -u gunicorn -f
# or the last 20 line
sudo journalctl -u gunicorn -f | tail -n 20
```

---

## References

- [Django + nginx + gunicorn](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu)
- [redis + celery](https://www.digitalocean.com/community/questions/how-to-set-up-django-app-redis-celery-a06db780-5335-493e-8158-7128ea7d2cc1)

---

**Last Updated:** $(date +%Y-%m-%d)
**Maintained By:** PackGuard

