# 🏗️ KHAZAD-DÛM PRODUCTION DEPLOYMENT GUIDE

## 🚀 Complete Production Infrastructure Built!

Your Khazad-dûm trading system is now equipped with enterprise-grade production infrastructure. This guide will walk you through deployment and management.

## 📋 What's Been Created

### ✅ Docker Infrastructure
- **Multi-stage Dockerfile** - Optimized Python 3.13 container with security best practices
- **Docker Compose** - Complete orchestration with PostgreSQL, Redis, Nginx, monitoring
- **Health Checks** - Comprehensive monitoring for all services
- **Volume Management** - Persistent storage for data, logs, and configurations

### ✅ Database Setup
- **PostgreSQL Schema** - Complete trading system database with pattern tracking
- **Database Views** - Optimized queries for active positions, patterns, daily summaries
- **Triggers & Functions** - Automated pattern performance calculation
- **Backup System** - Automated daily/weekly backups with retention

### ✅ Reverse Proxy & Security
- **Nginx Configuration** - SSL termination, WebSocket support, security headers
- **Rate Limiting** - API protection with configurable limits
- **SSL/TLS** - Modern encryption with automatic certificate management
- **Security Headers** - HSTS, CSP, XSS protection

### ✅ Monitoring & Observability
- **Health Check System** - Real-time monitoring of all components
- **Prometheus Integration** - Metrics collection and alerting
- **Log Aggregation** - Centralized logging with rotation
- **Performance Monitoring** - CPU, memory, disk usage tracking

### ✅ Automation & Maintenance
- **Makefile Commands** - Easy deployment and management
- **Maintenance Scripts** - Automated backups, cleanup, health checks
- **Cron Jobs** - Scheduled maintenance and monitoring
- **SSL Renewal** - Automatic certificate renewal

## 🎯 Quick Start Deployment

### 1. Initial Setup
```bash
# Copy the environment template
cp .env.example .env

# Edit with your API keys and passwords
nano .env

# Run initial setup
make setup
```

### 2. Configure Environment
Edit your `.env` file with:
- **OpenAI API Key** (required for TradingAgents)
- **Finnhub API Key** (required for market data)
- **Strong passwords** for database and Redis
- **Domain name** for SSL certificates
- **IBKR settings** (start with paper trading!)

### 3. Deploy System
```bash
# Build and start all services
make deploy

# Check system status
make status

# View logs
make logs

# Check health
make health
```

## 🌐 Access Points

After deployment, access your system at:

- **Trading Dashboard**: `https://your-domain.com/monitor/`
- **Health Check**: `https://your-domain.com/health`
- **Metrics (Prometheus)**: `http://your-domain.com:9090`
- **Grafana (optional)**: `http://your-domain.com:3000`
- **Development Mode**: `http://localhost:8080`

## 🔧 Management Commands

### Deployment Commands
```bash
make setup           # Initial setup (first time)
make build           # Build Docker images
make start           # Start all services
make stop            # Stop all services
make restart         # Restart all services
make deploy          # Full production deployment
```

### Monitoring Commands
```bash
make logs            # View all service logs
make health          # Check system health
make status          # Show container status
make monitor         # Start monitoring stack
make perf            # Show performance metrics
```

### Maintenance Commands
```bash
make backup          # Manual backup
make clean           # Clean Docker resources
make ssl             # Setup/renew SSL certificates
make update          # Update and restart system
```

### Development Commands
```bash
make test            # Run test suite
make dev             # Start development environment
make shell           # Open shell in trading engine
make db-shell        # Open database shell
make redis-cli       # Open Redis CLI
```

## 🏥 Health Monitoring

The system includes comprehensive health monitoring:

### Automated Health Checks
- **Database connectivity** and performance
- **Redis cache** availability and memory usage
- **Trading engine** core functionality
- **Pattern system** availability
- **API services** connectivity
- **Disk space** and memory usage
- **SSL certificates** expiration

### Health Check Endpoint
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Returns detailed status for all components with latency metrics.

## 💾 Backup & Recovery

### Automated Backups
- **Daily database backups** at 2:00 AM
- **Weekly full system backups** on Sundays
- **30-day retention** policy
- **Configuration backups** included

### Manual Backup
```bash
# Create backup
make backup

# View backups
ls -la deploy/backups/

# Restore from backup (manual process)
# See backup MANIFEST.txt for instructions
```

### Backup Contents
- PostgreSQL database dump (gzipped)
- Nginx configurations
- SSL certificates
- Environment settings
- Application configurations

## 🔐 Security Features

### Container Security
- **Non-root users** in all containers
- **Read-only configurations** mounted
- **Network segmentation** with custom bridge
- **Resource limits** and health checks
- **Secrets management** via environment variables

### Network Security
- **SSL/TLS termination** at proxy
- **Security headers** (HSTS, CSP, XSS protection)
- **Rate limiting** for APIs
- **Firewall-ready** configuration
- **Internal network isolation**

### Access Control
- **Database user** with limited permissions
- **Redis authentication** required
- **Nginx access controls** for metrics
- **SSL certificate** validation

## 📊 Performance Optimization

### Database Optimization
- **Indexed queries** for common operations
- **Connection pooling** via SQLAlchemy
- **Query optimization** with views
- **Automatic statistics** updates
- **Vacuum and analyze** scheduling

### Application Optimization
- **Multi-stage Docker builds** for smaller images
- **Python virtual environments** for dependencies
- **Caching with Redis** for hot data
- **Gzip compression** for web content
- **Static file serving** via Nginx

### System Optimization
- **Resource limits** per container
- **Log rotation** to prevent disk full
- **Docker cleanup** automation
- **Memory usage** monitoring
- **Disk space** alerting

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
make logs

# Check configuration
docker compose config

# Restart individual service
docker compose restart trading-engine
```

**Database connection failed:**
```bash
# Check database status
make db-shell

# Reset database
docker compose restart database
```

**SSL certificate issues:**
```bash
# Generate new certificates
make ssl

# Check certificate validity
openssl x509 -noout -dates -in deploy/ssl/fullchain.pem
```

**Health check failures:**
```bash
# Detailed health check
make health

# Check individual components
docker compose ps
docker compose logs trading-engine
```

### Log Locations
- **Application logs**: `logs/`
- **Container logs**: `docker compose logs [service]`
- **Nginx logs**: `/var/log/nginx/` (in container)
- **Database logs**: PostgreSQL container logs
- **Maintenance logs**: `logs/maintenance.log`

## 🔄 Updates and Maintenance

### Regular Maintenance
The system includes automated maintenance via cron jobs:
- **Daily**: Database backups, log rotation, health checks
- **Weekly**: Full system backup, Docker cleanup, SSL checks
- **Monthly**: Database optimization, old data cleanup

### Manual Updates
```bash
# Update system code
git pull
make update

# Rebuild containers
make build
make restart
```

### Monitoring Alerts
Set up monitoring alerts by configuring:
- **Email notifications** in crontab
- **Slack/Discord webhooks** in .env
- **Grafana alerts** in monitoring stack
- **Log-based alerts** for critical issues

## 🎛️ Configuration Reference

### Critical Configuration Files
- `.env` - Environment variables and secrets
- `docker-compose.yml` - Service orchestration
- `deploy/nginx/conf.d/khazad.conf` - Reverse proxy config
- `deploy/database/init.sql` - Database schema
- `config/settings/base_config.py` - Application settings

### Environment Variables
See `.env.example` for complete list:
- **API Keys**: OpenAI, Finnhub, optional others
- **Database**: PostgreSQL connection settings
- **Redis**: Cache configuration
- **Trading**: Risk management settings
- **Security**: SSL and authentication settings

## 🎉 Production Checklist

Before going live:

### Security Checklist
- [ ] Strong passwords in .env (20+ characters)
- [ ] SSL certificates configured
- [ ] API keys secured and valid
- [ ] Firewall rules configured
- [ ] Backup system tested
- [ ] Health monitoring setup

### Trading Safety Checklist
- [ ] Start with paper trading (`IBKR_PAPER_TRADING=true`)
- [ ] Conservative risk settings initially
- [ ] Monitor logs for first 24 hours
- [ ] Test with small position sizes
- [ ] Verify pattern system accuracy
- [ ] Set up trading alerts

### Operational Checklist
- [ ] Monitoring dashboards configured
- [ ] Backup restoration tested
- [ ] Maintenance cron jobs installed
- [ ] Log rotation working
- [ ] Health checks passing
- [ ] Performance baseline established

## 📞 Support & Resources

### Documentation
- **WARP.md** - Development guidance
- **README.md** - System overview
- **TradingAgents docs** - AI framework documentation
- **Docker Compose docs** - Container orchestration
- **PostgreSQL docs** - Database reference

### Monitoring Resources
- **Health endpoint**: `/health`
- **Metrics endpoint**: `/metrics` 
- **Log files**: `logs/` directory
- **Container stats**: `docker stats`
- **System performance**: `make perf`

---

## 🏆 You're Now Production Ready!

Your Khazad-dûm trading system now has:
- ✅ **Enterprise-grade infrastructure**
- ✅ **Automated monitoring and maintenance**
- ✅ **Security best practices**
- ✅ **Professional deployment automation**
- ✅ **Comprehensive backup system**
- ✅ **Production observability**

**Next Steps:**
1. Configure your `.env` file
2. Run `make deploy`
3. Monitor the system for 24-48 hours
4. Gradually increase position sizes
5. Set up monitoring alerts
6. Enjoy your professional trading system! 🚀

---

*"The Dwarves delved too greedily and too deep... but with proper DevOps, we won't awaken any Balrogs."* 🔥