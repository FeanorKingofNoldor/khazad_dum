# KHAZAD_DUM Docker Production Guide

> **🐳 Complete production deployment with Docker orchestration**

## 🎯 Current Production Setup

Your KHAZAD_DUM system is configured for **production-grade deployment** using Docker containers:

- **PostgreSQL 16** (containerized database)
- **Redis 7** (containerized caching)  
- **Docker networking** (isolated & secure)
- **Persistent volumes** (data survives container restarts)
- **Health checks** (automatic service monitoring)

---

## 🚀 Quick Start

### Start Infrastructure (Database + Cache)
```bash
# Start database and Redis (minimum required)
docker-compose up -d database redis

# Verify services are healthy
docker-compose ps

# Expected output:
# khazad-database   Up 2 minutes (healthy)
# khazad-redis      Up 2 minutes (healthy)
```

### Start Full Application Stack
```bash
# Start everything (if you have the full stack configured)
docker-compose up -d

# View all services
docker-compose ps

# Follow logs in real-time
docker-compose logs -f
```

---

## 🗄️ Database Operations

### PostgreSQL Container Management
```bash
# Connect to database directly
docker exec -it khazad-database psql -U khazad_user -d khazad_dum

# Execute SQL from host
docker exec khazad-database psql -U khazad_user -d khazad_dum -c "SELECT version();"

# Create database backup
docker exec khazad-database pg_dump -U khazad_user khazad_dum > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i khazad-database psql -U khazad_user -d khazad_dum < backup_file.sql

# Monitor database performance
docker exec khazad-database psql -U khazad_user -d khazad_dum -c "
SELECT schemaname,tablename,n_tup_ins,n_tup_upd,n_tup_del,n_tup_hot_upd 
FROM pg_stat_user_tables 
ORDER BY n_tup_ins DESC;
"
```

### Database Connection from Host
```bash
# External connection (from your Python scripts)
Host: localhost
Port: 5433  # External port (mapped from internal 5432)
Database: khazad_dum
User: khazad_user  
Password: khazad_secure_2024!

# Test connection
PGPASSWORD=khazad_secure_2024! psql -h localhost -p 5433 -U khazad_user -d khazad_dum
```

---

## 🔴 Redis Operations

### Redis Container Management
```bash
# Connect to Redis directly
docker exec -it khazad-redis redis-cli -a redis_secure_2024!

# Execute Redis commands from host
docker exec khazad-redis redis-cli -a redis_secure_2024! INFO server

# Monitor Redis performance
docker exec khazad-redis redis-cli -a redis_secure_2024! MONITOR

# Clear all cached data
docker exec khazad-redis redis-cli -a redis_secure_2024! FLUSHALL

# Check memory usage
docker exec khazad-redis redis-cli -a redis_secure_2024! INFO memory
```

### Redis Connection from Host
```bash
# External connection (from your Python scripts)
Host: localhost
Port: 6380  # External port (mapped from internal 6379)
Password: redis_secure_2024!

# Test connection
redis-cli -h localhost -p 6380 -a redis_secure_2024! ping
```

---

## 🔧 Container Management

### Service Control
```bash
# Start specific services
docker-compose up -d database redis

# Stop specific services
docker-compose stop database redis

# Restart services
docker-compose restart database redis

# Remove services (keeps volumes)
docker-compose rm -f database redis

# Start with fresh containers (rebuilds if needed)
docker-compose up -d --force-recreate database redis
```

### Viewing Logs
```bash
# View logs for specific service
docker-compose logs database
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f database
docker-compose logs -f redis

# View last 100 lines
docker-compose logs --tail=100 database

# View logs with timestamps
docker-compose logs -t database
```

### Resource Monitoring
```bash
# View resource usage for all containers
docker stats

# View resource usage for specific containers  
docker stats khazad-database khazad-redis

# View container details
docker inspect khazad-database
docker inspect khazad-redis
```

---

## 💾 Data Persistence

### Understanding Volumes
Your data is stored in **Docker volumes** that persist even when containers are recreated:

```yaml
# From docker-compose.yml
volumes:
  postgres_data:    # PostgreSQL data
    driver: local
  redis_data:       # Redis data  
    driver: local
```

### Volume Operations
```bash
# List all volumes
docker volume ls

# Inspect volume details
docker volume inspect khazad_dum_postgres_data
docker volume inspect khazad_dum_redis_data

# Backup volume data
docker run --rm -v khazad_dum_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume data  
docker run --rm -v khazad_dum_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres_backup.tar.gz -C /data
```

### Data Location on Host
```bash
# Find where Docker stores volume data
docker volume inspect khazad_dum_postgres_data | grep Mountpoint
docker volume inspect khazad_dum_redis_data | grep Mountpoint

# Typical locations:
# /var/lib/docker/volumes/khazad_dum_postgres_data/_data
# /var/lib/docker/volumes/khazad_dum_redis_data/_data
```

---

## 🌐 Network Configuration

### Understanding Docker Networks
Your containers communicate via the `khazad-network`:

```yaml
# From docker-compose.yml
networks:
  khazad-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Network Operations
```bash
# View network details
docker network inspect khazad_dum_khazad-network

# List containers on network
docker network inspect khazad_dum_khazad-network --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{end}}'

# Test connectivity between containers
docker exec khazad-database ping khazad-redis
docker exec khazad-redis ping khazad-database
```

### Port Mapping
```bash
# External ports (accessible from host)
PostgreSQL: localhost:5433 → container:5432
Redis:      localhost:6380 → container:6379

# Internal ports (container-to-container communication)
PostgreSQL: database:5432
Redis:      redis:6379

# Check port mapping
docker port khazad-database
docker port khazad-redis
```

---

## 🔧 Troubleshooting

### Common Issues

**Services not starting:**
```bash
# Check service status
docker-compose ps

# Check logs for errors
docker-compose logs database
docker-compose logs redis

# Restart services
docker-compose restart database redis
```

**Port conflicts:**
```bash
# Check what's using the ports
sudo netstat -tlnp | grep :5433
sudo netstat -tlnp | grep :6380

# If ports are in use, either:
# 1. Stop conflicting services
# 2. Change ports in docker-compose.yml
```

**Connection refused errors:**
```bash
# Ensure containers are healthy
docker-compose ps

# Test internal connectivity
docker exec khazad-database ping khazad-redis

# Check firewall settings
sudo ufw status
```

**Performance issues:**
```bash
# Check container resource usage
docker stats khazad-database khazad-redis

# Check system resources
htop
df -h

# Tune PostgreSQL if needed
docker exec khazad-database psql -U khazad_user -d khazad_dum -c "SHOW all;"
```

### Health Check Failures
```bash
# Check health status
docker inspect khazad-database | grep -A 10 Health
docker inspect khazad-redis | grep -A 10 Health

# Manual health checks
docker exec khazad-database pg_isready -U khazad_user -d khazad_dum
docker exec khazad-redis redis-cli -a redis_secure_2024! ping
```

### Data Recovery
```bash
# If containers are corrupted, but data is safe:
docker-compose down
docker-compose up -d --force-recreate

# If you need to reset everything (CAREFUL - loses data):
docker-compose down -v  # -v removes volumes too
docker-compose up -d
```

---

## 🔄 Maintenance Tasks

### Regular Maintenance
```bash
# Weekly: Update container images
docker-compose pull
docker-compose up -d --force-recreate

# Weekly: Clean up unused resources  
docker system prune -f
docker volume prune -f

# Monthly: Backup databases
docker exec khazad-database pg_dump -U khazad_user khazad_dum > monthly_backup_$(date +%Y%m%d).sql

# Monthly: Analyze database performance
docker exec khazad-database psql -U khazad_user -d khazad_dum -c "ANALYZE;"
```

### Performance Optimization
```bash
# PostgreSQL tuning
docker exec khazad-database psql -U khazad_user -d khazad_dum -c "
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
SELECT pg_reload_conf();
"

# Redis tuning
docker exec khazad-redis redis-cli -a redis_secure_2024! CONFIG SET maxmemory 512mb
docker exec khazad-redis redis-cli -a redis_secure_2024! CONFIG SET maxmemory-policy allkeys-lru
```

---

## 🚨 Production Deployment Checklist

### Security
- [ ] **Strong passwords** set in `.env` file
- [ ] **Firewall configured** (only expose necessary ports)
- [ ] **SSL/TLS encryption** for external connections
- [ ] **Regular security updates** for container images

### Monitoring  
- [ ] **Health checks** working for all services
- [ ] **Log aggregation** configured
- [ ] **Alerting** set up for service failures
- [ ] **Resource monitoring** (CPU, memory, disk)

### Backup & Recovery
- [ ] **Automated database backups** scheduled
- [ ] **Volume backups** configured
- [ ] **Recovery procedures** tested
- [ ] **Backup retention policy** defined

### Performance
- [ ] **Resource limits** set for containers
- [ ] **Database tuning** applied
- [ ] **Connection pooling** configured
- [ ] **Cache policies** optimized

---

## 📖 Docker Compose Reference

### Key Services Configuration
```yaml
# Current production setup
services:
  database:
    image: postgres:16-alpine
    container_name: khazad-database
    ports:
      - "5433:5432"    # External:Internal
    environment:
      POSTGRES_DB: khazad_dum
      POSTGRES_USER: khazad_user  
      POSTGRES_PASSWORD: khazad_secure_2024!
    
  redis:
    image: redis:7-alpine
    container_name: khazad-redis
    ports:
      - "6380:6379"    # External:Internal  
    command: redis-server --appendonly yes --requirepass redis_secure_2024!
```

### Environment Variables
```bash
# Database configuration
DATABASE_URL=postgresql://khazad_user:khazad_secure_2024!@localhost:5433/khazad_dum
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

# Redis configuration  
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=redis_secure_2024!
```

---

*🎯 **Your setup is production-ready!** The containerized infrastructure provides isolation, scalability, and easy deployment across different environments.*