# Deployment Guide for Dropout Prediction System

This guide covers different deployment options for the AI-based Dropout Prediction & Counseling System.

## Table of Contents
1. [Local Development Setup](#local-development-setup)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [Security Considerations](#security-considerations)

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dropout-prediction-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the setup script**
   ```bash
   python run.py
   ```

This will automatically:
- Check and install dependencies
- Initialize the database
- Train the ML model (if needed)
- Start the Flask application

### Manual Setup
If you prefer manual setup:

1. **Initialize database**
   ```bash
   python init_db.py
   ```

2. **Train ML model**
   ```bash
   python train_model.py
   ```

3. **Start application**
   ```bash
   python app.py
   ```

## Production Deployment

### Using Gunicorn (Recommended)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn configuration**
   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:5000"
   workers = 4
   worker_class = "sync"
   timeout = 120
   keepalive = 2
   max_requests = 1000
   max_requests_jitter = 100
   preload_app = True
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -c gunicorn.conf.py app:app
   ```

### Using uWSGI

1. **Install uWSGI**
   ```bash
   pip install uwsgi
   ```

2. **Create uWSGI configuration**
   ```ini
   # uwsgi.ini
   [uwsgi]
   module = app:app
   master = true
   processes = 4
   socket = /tmp/dropout-prediction.sock
   chmod-socket = 666
   vacuum = true
   die-on-term = true
   ```

3. **Run with uWSGI**
   ```bash
   uwsgi --ini uwsgi.ini
   ```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_db.py
RUN python train_model.py

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/dropout_prediction
    depends_on:
      - db
    volumes:
      - ./models:/app/models

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: dropout_prediction
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Build and Run
```bash
docker-compose up --build
```

## Cloud Deployment

### Heroku Deployment

1. **Create Procfile**
   ```
   web: gunicorn app:app
   release: python init_db.py
   ```

2. **Create runtime.txt**
   ```
   python-3.9.18
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   ```

### AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 20.04 LTS)

2. **Install dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx supervisor
   ```

3. **Clone and setup application**
   ```bash
   git clone <repository-url>
   cd dropout-prediction-system
   pip3 install -r requirements.txt
   python3 init_db.py
   python3 train_model.py
   ```

4. **Configure Supervisor**
   ```ini
   # /etc/supervisor/conf.d/dropout-prediction.conf
   [program:dropout-prediction]
   command=/home/ubuntu/dropout-prediction-system/venv/bin/gunicorn -c gunicorn.conf.py app:app
   directory=/home/ubuntu/dropout-prediction-system
   user=ubuntu
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/dropout-prediction.log
   ```

### Google Cloud Platform

1. **Create app.yaml**
   ```yaml
   runtime: python39
   
   env_variables:
     SECRET_KEY: your-secret-key
     DATABASE_URL: your-database-url
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

## Environment Configuration

### Production Environment Variables
```bash
# Security
SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://username:password@localhost/dropout_prediction

# Email (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# ML Model
MODEL_RETRAIN_INTERVAL_DAYS=30
HIGH_RISK_THRESHOLD=0.7
MEDIUM_RISK_THRESHOLD=0.4

# Security
SESSION_TIMEOUT_HOURS=8
MAX_LOGIN_ATTEMPTS=5
```

## Database Setup

### SQLite (Development)
- Automatically created
- File: `dropout_prediction.db`
- No additional setup required

### PostgreSQL (Production)

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

2. **Create database and user**
   ```sql
   CREATE DATABASE dropout_prediction;
   CREATE USER dropout_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE dropout_prediction TO dropout_user;
   ```

3. **Update DATABASE_URL**
   ```bash
   DATABASE_URL=postgresql://dropout_user:secure_password@localhost/dropout_prediction
   ```

### MySQL (Alternative)

1. **Install MySQL**
   ```bash
   sudo apt install mysql-server
   ```

2. **Create database**
   ```sql
   CREATE DATABASE dropout_prediction;
   CREATE USER 'dropout_user'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON dropout_prediction.* TO 'dropout_user'@'localhost';
   ```

3. **Install MySQL connector**
   ```bash
   pip install PyMySQL
   ```

4. **Update DATABASE_URL**
   ```bash
   DATABASE_URL=mysql+pymysql://dropout_user:secure_password@localhost/dropout_prediction
   ```

## Security Considerations

### SSL/HTTPS Setup
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        # ... other proxy settings
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Security Headers
Add to Nginx configuration:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### Firewall Configuration
```bash
# Ubuntu UFW
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Regular Backups
```bash
# Database backup script
#!/bin/bash
pg_dump dropout_prediction > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Monitoring and Logging
```python
# Add to app.py for production logging
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/dropout_prediction.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Dropout Prediction System startup')
```

## Performance Optimization

### Caching
```python
# Install Flask-Caching
pip install Flask-Caching

# Add to app.py
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def get_analytics_data():
    # Expensive analytics calculation
    pass
```

### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_student_risk_category ON student(risk_category);
CREATE INDEX idx_student_last_prediction ON student(last_prediction_date);
CREATE INDEX idx_notification_counselor ON notification(counselor_id, is_read);
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission denied**
   ```bash
   sudo chown -R $USER:$USER /path/to/app
   chmod +x run.py
   ```

3. **Database connection error**
   - Check DATABASE_URL format
   - Verify database server is running
   - Check firewall settings

4. **ML model not loading**
   ```bash
   python train_model.py  # Retrain model
   ```

### Log Locations
- Application logs: `/var/log/dropout-prediction.log`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

## Maintenance

### Regular Tasks
1. **Update dependencies** (monthly)
   ```bash
   pip list --outdated
   pip install -U package_name
   ```

2. **Retrain ML model** (monthly)
   ```bash
   python train_model.py
   ```

3. **Database cleanup** (weekly)
   ```sql
   DELETE FROM notification WHERE created_at < NOW() - INTERVAL '30 days';
   ```

4. **Backup verification** (weekly)
   ```bash
   pg_restore --list backup_file.sql
   ```

For additional support or questions, please refer to the README.md file or contact the development team.
