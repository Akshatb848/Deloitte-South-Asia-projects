# Deployment Guide

## Education Intelligence Dashboard
**Ministry of Education, Government of India**

---

## Deployment Scenarios

### 1. Local Development

**Requirements**
- Docker Desktop
- 8GB RAM
- 10GB disk space

**Steps**
```bash
# Clone repository
git clone https://github.com/Akshatb848/Deloitte-South-Asia-projects.git
cd Deloitte-South-Asia-projects

# Run setup script
chmod +x setup.sh
./setup.sh
```

---

### 2. Production Server Deployment

#### Option A: Docker Compose (Recommended)

**Server Requirements**
- Ubuntu 20.04+ / RHEL 8+ / Debian 11+
- 16GB RAM
- 50GB disk space
- Public IP address
- Domain name (optional)

**Steps**

1. **Prepare Server**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Install Docker Compose
   sudo apt install docker-compose -y

   # Add user to docker group
   sudo usermod -aG docker $USER
   ```

2. **Clone and Configure**
   ```bash
   git clone https://github.com/Akshatb848/Deloitte-South-Asia-projects.git
   cd Deloitte-South-Asia-projects

   # Create production environment
   cp .env.example .env.production
   nano .env.production
   ```

3. **Configure SSL (Let's Encrypt)**
   ```bash
   # Install certbot
   sudo apt install certbot python3-certbot-nginx -y

   # Obtain certificate
   sudo certbot certonly --standalone -d yourdomain.gov.in

   # Update nginx.conf with SSL
   ```

4. **Deploy**
   ```bash
   docker-compose -f docker-compose.yml up -d

   # Pull LLM model
   docker exec education-dashboard-ollama ollama pull mistral:7b-instruct

   # Check status
   docker-compose ps
   ```

5. **Configure Firewall**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

---

### 3. Cloud Deployment

#### AWS Deployment

**Architecture**
- EC2 instance (t3.xlarge or better)
- Application Load Balancer
- Route 53 for DNS
- S3 for static assets
- CloudWatch for monitoring

**Steps**

1. **Launch EC2 Instance**
   ```bash
   # Use Ubuntu 22.04 LTS AMI
   # Instance type: t3.xlarge (4 vCPU, 16GB RAM)
   # Storage: 50GB GP3
   # Security Group: Allow 80, 443, 22
   ```

2. **Install Dependencies**
   ```bash
   ssh -i key.pem ubuntu@ec2-instance

   # Install Docker
   curl -fsSL https://get.docker.com | sh

   # Install Docker Compose
   sudo apt install docker-compose -y
   ```

3. **Deploy Application**
   ```bash
   git clone https://github.com/Akshatb848/Deloitte-South-Asia-projects.git
   cd Deloitte-South-Asia-projects

   # Configure environment
   cp .env.example .env
   # Edit .env with production settings

   # Start services
   docker-compose up -d
   ```

4. **Configure Load Balancer**
   - Create Application Load Balancer
   - Configure Target Group (port 8080)
   - Add health check: `/api/health`
   - Configure SSL certificate

---

### 4. Kubernetes Deployment

**Requirements**
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.x

**Deployment**

1. **Create Namespace**
   ```bash
   kubectl create namespace education-dashboard
   ```

2. **Create ConfigMap**
   ```bash
   kubectl create configmap dashboard-config \
     --from-file=data/newsletter_data.json \
     -n education-dashboard
   ```

3. **Create Secrets**
   ```bash
   kubectl create secret generic dashboard-secrets \
     --from-literal=api-key=your-secure-key \
     -n education-dashboard
   ```

4. **Deploy Application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

5. **Verify Deployment**
   ```bash
   kubectl get pods -n education-dashboard
   kubectl get svc -n education-dashboard
   ```

---

## Post-Deployment Configuration

### 1. SSL/TLS Setup

**Let's Encrypt (Free)**
```bash
# Install certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.gov.in

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

**Custom Certificate**
```bash
# Place certificates
sudo cp your-cert.crt /etc/ssl/certs/
sudo cp your-key.key /etc/ssl/private/

# Update nginx.conf
ssl_certificate /etc/ssl/certs/your-cert.crt;
ssl_certificate_key /etc/ssl/private/your-key.key;
```

---

### 2. Monitoring Setup

**Prometheus + Grafana**
```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure_password
```

**Health Monitoring**
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  curl -f http://localhost:8000/api/health || echo "Backend unhealthy"
  sleep 60
done
EOF

chmod +x monitor.sh
```

---

### 3. Backup Strategy

**Database Backup**
```bash
# Backup vector database
tar -czf vector_db_backup_$(date +%Y%m%d).tar.gz vector_db/

# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env config/
```

**Automated Backup**
```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

---

### 4. Log Management

**Configure Log Rotation**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/education-dashboard

/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

**Centralized Logging**
```bash
# Use ELK stack or cloud logging
docker-compose -f docker-compose.elk.yml up -d
```

---

## Performance Tuning

### 1. LLM Optimization

**Use Quantized Models**
```bash
# Pull quantized model (faster, less memory)
ollama pull mistral:7b-instruct-q4_K_M
```

**Configure Model Parameters**
```python
# In llm_handler.py
"options": {
    "num_thread": 8,  # Use all CPU cores
    "num_gpu": 1,     # Use GPU if available
    "num_batch": 512  # Batch size
}
```

---

### 2. Vector Database Optimization

**Pre-build Index**
```bash
# Build index before deployment
python -c "
from backend.rag.rag_system import RAGSystem
import asyncio
rag = RAGSystem()
asyncio.run(rag.initialize())
"
```

**Use GPU-accelerated FAISS**
```bash
# Install FAISS-GPU
pip install faiss-gpu
```

---

### 3. Frontend Optimization

**Enable CDN**
```nginx
# Update nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    # Add CDN configuration
}
```

**Minify Assets**
```bash
# Install minification tools
npm install -g terser csso-cli

# Minify JS
terser frontend/js/app.js -o frontend/js/app.min.js

# Minify CSS
csso frontend/css/style.css -o frontend/css/style.min.css
```

---

## Security Hardening

### 1. Firewall Configuration

**UFW (Ubuntu)**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

**iptables**
```bash
# Allow HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

---

### 2. Rate Limiting

**Nginx Rate Limiting**
```nginx
# Add to nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20;
}
```

---

### 3. Authentication (Optional)

**OAuth 2.0 Integration**
```python
# Add to main.py
from fastapi_oauth2 import OAuth2

oauth2 = OAuth2(
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

---

## Troubleshooting

### Common Deployment Issues

**1. Port Already in Use**
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

**2. Out of Memory**
```bash
# Increase Docker memory
docker update --memory="8g" education-dashboard-backend

# Use swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**3. LLM Model Not Loading**
```bash
# Check Ollama logs
docker logs education-dashboard-ollama

# Manually pull model
docker exec -it education-dashboard-ollama bash
ollama pull mistral:7b-instruct
```

---

## Maintenance

### Regular Tasks

**Daily**
- Check application health
- Monitor error logs
- Review API usage

**Weekly**
- Update vector database if data changed
- Review performance metrics
- Check disk space

**Monthly**
- Update dependencies
- Security patch review
- Backup verification
- Performance audit

---

## Scaling

### Horizontal Scaling

**Load Balancer Configuration**
```nginx
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

**Docker Swarm**
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml education-dashboard

# Scale services
docker service scale education-dashboard_backend=3
```

---

## Contact

**Deployment Support**: devops@deloitte.com
**Technical Issues**: education-dashboard@deloitte.com
**Emergency Hotline**: +91-XXXX-XXXXXX

---

**Last Updated**: February 11, 2026
