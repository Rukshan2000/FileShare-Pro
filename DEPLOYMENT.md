# Production Deployment Guide

This guide covers deploying FileShare Pro in a production environment with security best practices.

## 🚀 Quick Production Setup

### Prerequisites

- Python 3.8 or higher
- Reverse proxy (nginx/Apache)
- SSL certificate
- Firewall configured
- Monitoring tools

### Basic Production Deployment

1. **Clone and Setup**
   ```bash
   git clone https://github.com/Rukshan2000/FileShare-Pro.git
   cd FileShare-Pro
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Create production config
   cp config.example.py config.py
   # Edit config.py with production settings
   ```

3. **Set Up Systemd Service**
   ```bash
   sudo cp deployment/fileshare.service /etc/systemd/system/
   sudo systemctl enable fileshare
   sudo systemctl start fileshare
   ```

## 🔒 Security Configuration

### 1. Environment Variables

Create a `.env` file with:

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
ADMIN_KEY=your-admin-api-key-here
UPLOAD_FOLDER=/var/www/fileshare/uploads
MAX_CONTENT_LENGTH=104857600  # 100MB
```

### 2. Nginx Configuration

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # File upload limits
    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static files directly
    location /static {
        alias /path/to/FileShare-Pro/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Firewall Rules

```bash
# Allow SSH, HTTP, and HTTPS
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Block direct access to application port
sudo ufw deny 8000
```

## 📊 Monitoring and Logging

### Log Configuration

Configure logging in your production app:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/fileshare.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Health Check Endpoint

Add a health check endpoint:

```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

### Monitoring Setup

Consider using:
- **Uptime monitoring**: Pingdom, UptimeRobot
- **Application monitoring**: New Relic, DataDog
- **Log aggregation**: ELK Stack, Fluentd
- **Metrics**: Prometheus + Grafana

## 🔄 Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/fileshare"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/fileshare/uploads

# Backup configuration files
cp /var/www/fileshare/users.json $BACKUP_DIR/users_$DATE.json
cp /var/www/fileshare/files_metadata.json $BACKUP_DIR/metadata_$DATE.json

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.json" -mtime +30 -delete
```

Add to crontab for daily backups:
```bash
0 2 * * * /path/to/backup.sh
```

## 🔧 Performance Optimization

### 1. Production WSGI Server

Replace Flask's dev server with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 2. Redis for Session Storage

```python
# config.py
REDIS_URL = 'redis://localhost:6379/0'
SESSION_TYPE = 'redis'
```

### 3. CDN for Static Files

Consider using a CDN for static assets:
- AWS CloudFront
- Cloudflare
- MaxCDN

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  fileshare:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./config:/app/config
    environment:
      - FLASK_ENV=production
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - fileshare
    restart: unless-stopped
```

## 📋 Production Checklist

Before going live:

- [ ] SSL certificate installed and configured
- [ ] Firewall rules configured
- [ ] Strong secrets configured (SECRET_KEY, ADMIN_KEY)
- [ ] Debug mode disabled
- [ ] Error logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Health checks configured
- [ ] Rate limiting implemented
- [ ] File upload validation strengthened
- [ ] Regular security updates scheduled
- [ ] Documentation updated with production URLs

## 🚨 Troubleshooting

### Common Issues

1. **Permission Errors**
   ```bash
   sudo chown -R www-data:www-data /var/www/fileshare
   sudo chmod -R 755 /var/www/fileshare
   ```

2. **Port Already in Use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

3. **SSL Certificate Issues**
   ```bash
   # Test certificate
   openssl x509 -in cert.pem -text -noout

   # Verify SSL setup
   openssl s_client -connect your-domain.com:443
   ```

### Log Locations

- Application logs: `/var/log/fileshare/`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

For additional support, please check our [troubleshooting guide](TROUBLESHOOTING.md) or create an issue on GitHub.
