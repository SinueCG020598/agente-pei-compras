# Guía de Deployment

Esta guía cubre el deployment del sistema PEI Compras AI en diferentes entornos.

## Tabla de Contenidos

- [Desarrollo Local](#desarrollo-local)
- [Staging](#staging)
- [Producción](#producción)
- [Docker](#docker)
- [Cloud Providers](#cloud-providers)
- [Monitoreo](#monitoreo)
- [Backups](#backups)

## Desarrollo Local

### Requisitos

- Python 3.11+
- Docker y Docker Compose
- Git

### Setup

```bash
# Clonar repositorio
git clone https://github.com/pei/pei-compras-ai.git
cd pei-compras-ai

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
make install-dev

# Configurar variables de entorno
cp .env.example .env
nano .env  # Completar con credenciales reales

# Levantar servicios externos
make docker-up

# Setup inicial
make setup

# Verificar instalación
python scripts/test_setup.py
```

### Ejecutar

```bash
# Terminal 1: API Backend
make run-api

# Terminal 2: Frontend
make run-frontend

# Terminal 3: Evolution API (WhatsApp)
docker logs -f pei-evolution-api
```

## Staging

### Infraestructura

- 1 servidor Ubuntu 22.04 LTS
- 4GB RAM mínimo
- 50GB storage
- Docker instalado

### Deployment

```bash
# En el servidor staging
cd /opt/pei-compras-ai

# Pull latest code
git pull origin develop

# Rebuild containers
docker-compose -f docker-compose.staging.yml build

# Restart services
docker-compose -f docker-compose.staging.yml up -d

# Run migrations
docker-compose -f docker-compose.staging.yml exec api alembic upgrade head

# Verificar estado
docker-compose -f docker-compose.staging.yml ps
```

### docker-compose.staging.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pei_user:${DB_PASSWORD}@postgres:5432/pei_compras
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: always

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    depends_on:
      - api
    restart: always

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=pei_compras
      - POSTGRES_USER=pei_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  evolution-api:
    image: atendai/evolution-api:latest
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}
    volumes:
      - evolution_data:/evolution
    restart: always

volumes:
  postgres_data:
  evolution_data:
```

## Producción

### Infraestructura Recomendada

#### Opción 1: Single Server (Pequeña Escala)

- VPS con Ubuntu 22.04 LTS
- 8GB RAM
- 100GB SSD
- Nginx como reverse proxy
- Certbot para SSL

#### Opción 2: Multi-Server (Media Escala)

- Load Balancer (HAProxy/Nginx)
- 2+ App Servers (API + Frontend)
- 1 Database Server (PostgreSQL)
- 1 Redis Server
- 1 Evolution API Server

#### Opción 3: Kubernetes (Gran Escala)

- Kubernetes cluster (GKE/EKS/AKS)
- Horizontal pod autoscaling
- Managed database (Cloud SQL/RDS)
- Managed Redis (ElastiCache/Memorystore)

### Deployment con Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build y Push

```bash
# Build image
docker build -t pei-compras-ai:latest .

# Tag for registry
docker tag pei-compras-ai:latest registry.example.com/pei-compras-ai:latest

# Push to registry
docker push registry.example.com/pei-compras-ai:latest
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/pei-compras-ai

upstream api_backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:8501;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.pei-compras.com app.pei-compras.com;
    return 301 https://$server_name$request_uri;
}

# API Backend
server {
    listen 443 ssl http2;
    server_name api.pei-compras.com;

    ssl_certificate /etc/letsencrypt/live/api.pei-compras.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.pei-compras.com/privkey.pem;

    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 443 ssl http2;
    server_name app.pei-compras.com;

    ssl_certificate /etc/letsencrypt/live/app.pei-compras.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.pei-compras.com/privkey.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### SSL con Let's Encrypt

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.pei-compras.com -d app.pei-compras.com

# Auto-renewal (ya configurado)
sudo systemctl status certbot.timer
```

## Cloud Providers

### AWS

#### Opción 1: EC2 + RDS

```bash
# EC2 Instance
# - Type: t3.medium (2 vCPU, 4GB RAM)
# - AMI: Ubuntu 22.04 LTS
# - Security Group: Allow 80, 443, 22

# RDS Database
# - Engine: PostgreSQL 15
# - Instance: db.t3.micro
# - Storage: 20GB SSD
# - Automated backups enabled

# ElastiCache (Redis)
# - Node type: cache.t3.micro
# - Engine: Redis 7
```

#### Deployment Script

```bash
#!/bin/bash
# deploy-aws.sh

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/pei/pei-compras-ai.git
cd pei-compras-ai

# Configure environment
cp .env.example .env
# Edit .env with production values

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Setup Nginx
sudo apt-get install nginx -y
sudo cp nginx.conf /etc/nginx/sites-available/pei-compras-ai
sudo ln -s /etc/nginx/sites-available/pei-compras-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Google Cloud Platform (GCP)

```bash
# Compute Engine + Cloud SQL
gcloud compute instances create pei-compras-ai \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB

# Cloud SQL
gcloud sql instances create pei-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Cloud Storage for backups
gsutil mb gs://pei-compras-backups
```

### Azure

```bash
# App Service + Azure Database for PostgreSQL
az appservice plan create \
  --name pei-compras-plan \
  --resource-group pei-rg \
  --sku B1 \
  --is-linux

az webapp create \
  --resource-group pei-rg \
  --plan pei-compras-plan \
  --name pei-compras-api \
  --runtime "PYTHON:3.11"

az postgres server create \
  --resource-group pei-rg \
  --name pei-postgres \
  --sku-name B_Gen5_1
```

## Kubernetes

### Deployment YAML

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pei-compras-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pei-compras-api
  template:
    metadata:
      labels:
        app: pei-compras-api
    spec:
      containers:
      - name: api
        image: registry.example.com/pei-compras-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pei-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: pei-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pei-compras-api
spec:
  selector:
    app: pei-compras-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic pei-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=openai-api-key="sk-..."

# Apply deployment
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/pei-compras-api
```

## Monitoreo

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

### Health Checks

```python
# src/api/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    # Check database connection
    # Check OpenAI API
    # Check other dependencies
    return {"status": "ready"}
```

## Backups

### Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup database
pg_dump -h localhost -U pei_user pei_compras | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup files
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /app/uploads

# Upload to S3 (opcional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://pei-backups/
aws s3 cp $BACKUP_DIR/files_$DATE.tar.gz s3://pei-backups/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

### Cron Job

```bash
# Agregar a crontab
crontab -e

# Backup diario a las 2 AM
0 2 * * * /opt/pei-compras-ai/backup.sh
```

## Rollback

### Docker

```bash
# Ver versiones anteriores
docker images pei-compras-ai

# Rollback a versión anterior
docker-compose stop api
docker tag pei-compras-ai:v1.0.0 pei-compras-ai:latest
docker-compose up -d api
```

### Kubernetes

```bash
# Ver historial
kubectl rollout history deployment/pei-compras-api

# Rollback
kubectl rollout undo deployment/pei-compras-api

# Rollback a versión específica
kubectl rollout undo deployment/pei-compras-api --to-revision=2
```

## Troubleshooting

### Logs

```bash
# Docker
docker-compose logs -f api

# Kubernetes
kubectl logs -f deployment/pei-compras-api

# Nginx
sudo tail -f /var/log/nginx/error.log
```

### Common Issues

#### Error: Connection to database failed

**Solución**: Verificar DATABASE_URL y conectividad

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

#### Error: OpenAI API rate limit

**Solución**: Implementar backoff y cache

#### High memory usage

**Solución**: Aumentar recursos o optimizar queries

---

**Última actualización**: 2025-11-06
**Versión**: 1.0
