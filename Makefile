# ==============================================================================
# KHAZAD-DÛM TRADING SYSTEM - PRODUCTION MAKEFILE
# Easy deployment and management commands
# ==============================================================================

# Default environment
ENV ?= production
COMPOSE_FILE ?= docker-compose.yml
PROJECT_NAME = khazad-dum

# Colors for output
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m
RESET := \033[0m

.PHONY: help setup build start stop restart logs clean backup restore ssl health test deploy

# Default target
help:
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BLUE)║                    KHAZAD-DÛM TRADING SYSTEM COMMANDS                        ║$(RESET)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(GREEN)🚀 DEPLOYMENT COMMANDS:$(RESET)"
	@echo "  $(YELLOW)make setup$(RESET)           - Initial setup (first time only)"
	@echo "  $(YELLOW)make build$(RESET)           - Build all Docker images"
	@echo "  $(YELLOW)make start$(RESET)           - Start all services"
	@echo "  $(YELLOW)make stop$(RESET)            - Stop all services"
	@echo "  $(YELLOW)make restart$(RESET)         - Restart all services"
	@echo "  $(YELLOW)make deploy$(RESET)          - Full production deployment"
	@echo ""
	@echo "$(GREEN)📊 MONITORING COMMANDS:$(RESET)"
	@echo "  $(YELLOW)make logs$(RESET)            - View all service logs"
	@echo "  $(YELLOW)make health$(RESET)          - Check system health"
	@echo "  $(YELLOW)make monitor$(RESET)         - Start monitoring stack"
	@echo "  $(YELLOW)make status$(RESET)          - Show container status"
	@echo ""
	@echo "$(GREEN)🔧 MAINTENANCE COMMANDS:$(RESET)"
	@echo "  $(YELLOW)make backup$(RESET)          - Backup database and configs"
	@echo "  $(YELLOW)make restore$(RESET)         - Restore from backup"
	@echo "  $(YELLOW)make ssl$(RESET)             - Setup/renew SSL certificates"
	@echo "  $(YELLOW)make clean$(RESET)           - Clean unused Docker resources"
	@echo ""
	@echo "$(GREEN)🧪 DEVELOPMENT COMMANDS:$(RESET)"
	@echo "  $(YELLOW)make test$(RESET)            - Run test suite"
	@echo "  $(YELLOW)make dev$(RESET)             - Start development environment"
	@echo "  $(YELLOW)make shell$(RESET)           - Open shell in trading engine"

# ==============================================================================
# SETUP AND DEPLOYMENT
# ==============================================================================

setup:
	@echo "$(GREEN)🔧 Setting up Khazad-dûm Production Environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📋 Creating .env file from template...$(RESET)"; \
		cp .env.example .env; \
		echo "$(RED)⚠️  IMPORTANT: Edit .env file with your API keys and passwords!$(RESET)"; \
	fi
	@echo "$(YELLOW)📁 Creating required directories...$(RESET)"
	@mkdir -p deploy/{ssl,backups} logs data cache results
	@echo "$(YELLOW)🔐 Setting up SSL directory permissions...$(RESET)"
	@chmod 700 deploy/ssl
	@echo "$(GREEN)✅ Setup complete! Edit .env file and run 'make deploy'$(RESET)"

build:
	@echo "$(GREEN)🏗️  Building Docker images...$(RESET)"
	docker compose -f $(COMPOSE_FILE) build --no-cache

start:
	@echo "$(GREEN)🚀 Starting Khazad-dûm services...$(RESET)"
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Services started! Check status with 'make status'$(RESET)"

stop:
	@echo "$(YELLOW)⏹️  Stopping all services...$(RESET)"
	docker compose -f $(COMPOSE_FILE) down

restart:
	@echo "$(YELLOW)🔄 Restarting all services...$(RESET)"
	docker compose -f $(COMPOSE_FILE) restart
	@echo "$(GREEN)✅ Services restarted!$(RESET)"

deploy: setup build start
	@echo "$(GREEN)🎉 Khazad-dûm deployed successfully!$(RESET)"
	@echo "$(BLUE)📊 Dashboard: https://your-domain.com/monitor/$(RESET)"
	@echo "$(BLUE)📈 Metrics: http://your-domain.com:9090$(RESET)"
	@echo "$(BLUE)🔍 Health: https://your-domain.com/health$(RESET)"

# ==============================================================================
# MONITORING AND LOGGING
# ==============================================================================

logs:
	@echo "$(GREEN)📜 Showing service logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f --tail=100

logs-trading:
	@echo "$(GREEN)📜 Trading engine logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f trading-engine

logs-monitor:
	@echo "$(GREEN)📜 Monitor dashboard logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f monitor-dashboard

logs-nginx:
	@echo "$(GREEN)📜 Nginx logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f nginx

logs-web:
	@echo "$(GREEN)📜 Web dashboard logs...$(RESET)"
	docker compose -f $(COMPOSE_FILE) logs -f web-dashboard

status:
	@echo "$(GREEN)📊 Container status:$(RESET)"
	@docker compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "$(GREEN)💾 Volume usage:$(RESET)"
	@docker system df
	@echo ""
	@echo "$(GREEN)🌐 Network info:$(RESET)"
	@docker network ls | grep khazad

health:
	@echo "$(GREEN)🏥 Checking system health...$(RESET)"
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "$(RED)❌ Health check failed$(RESET)"

monitor:
	@echo "$(GREEN)📊 Starting monitoring stack...$(RESET)"
	docker compose -f $(COMPOSE_FILE) --profile monitoring up -d
	@echo "$(BLUE)📈 Grafana: http://localhost:3000$(RESET)"
	@echo "$(BLUE)📊 Prometheus: http://localhost:9090$(RESET)"

# ==============================================================================
# MAINTENANCE
# ==============================================================================

backup:
	@echo "$(GREEN)💾 Creating backup...$(RESET)"
	@mkdir -p deploy/backups/$(shell date +%Y%m%d_%H%M%S)
	@echo "$(YELLOW)📊 Backing up database...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec -T database pg_dump -U khazad_user khazad_dum | gzip > deploy/backups/$(shell date +%Y%m%d_%H%M%S)/database.sql.gz
	@echo "$(YELLOW)📁 Backing up configurations...$(RESET)"
	@cp -r deploy/nginx deploy/backups/$(shell date +%Y%m%d_%H%M%S)/
	@cp .env deploy/backups/$(shell date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
	@echo "$(GREEN)✅ Backup completed in deploy/backups/$(shell date +%Y%m%d_%H%M%S)$(RESET)"

restore:
	@echo "$(YELLOW)📋 Available backups:$(RESET)"
	@ls -la deploy/backups/ 2>/dev/null || echo "No backups found"
	@echo "$(RED)⚠️  Manual restore required - check backup directory$(RESET)"

ssl:
	@echo "$(GREEN)🔐 Setting up SSL certificates...$(RESET)"
	@if [ ! -f deploy/ssl/fullchain.pem ]; then \
		echo "$(YELLOW)📜 Generating self-signed certificates for development...$(RESET)"; \
		openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
			-keyout deploy/ssl/privkey.pem \
			-out deploy/ssl/fullchain.pem \
			-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"; \
		echo "$(BLUE)📋 For production, replace with Let's Encrypt certificates$(RESET)"; \
	else \
		echo "$(GREEN)✅ SSL certificates already exist$(RESET)"; \
	fi

clean:
	@echo "$(YELLOW)🧹 Cleaning unused Docker resources...$(RESET)"
	docker system prune -f
	docker volume prune -f
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

# ==============================================================================
# DEVELOPMENT
# ==============================================================================

test:
	@echo "$(GREEN)🧪 Running test suite...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec trading-engine python -m pytest tests/ -v
	@echo "$(GREEN)✅ Tests completed$(RESET)"

dev:
	@echo "$(GREEN)🛠️  Starting development environment...$(RESET)"
	@COMPOSE_FILE=docker-compose.dev.yml $(MAKE) start
	@echo "$(BLUE)📊 Dev Dashboard: http://localhost:8080$(RESET)"

shell:
	@echo "$(GREEN)🐚 Opening shell in trading engine...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec trading-engine /bin/bash

# ==============================================================================
# UTILITY COMMANDS
# ==============================================================================

update:
	@echo "$(GREEN)⬆️  Updating system...$(RESET)"
	git pull
	$(MAKE) build
	$(MAKE) restart
	@echo "$(GREEN)✅ System updated$(RESET)"

reset:
	@echo "$(RED)⚠️  Resetting entire system (THIS WILL DELETE ALL DATA)$(RESET)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	docker compose -f $(COMPOSE_FILE) down -v
	docker system prune -af --volumes
	$(MAKE) setup

# SSL certificate renewal (for Let's Encrypt)
ssl-renew:
	@echo "$(GREEN)🔄 Renewing SSL certificates...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec nginx nginx -t && docker compose -f $(COMPOSE_FILE) exec nginx nginx -s reload
	@echo "$(GREEN)✅ SSL certificates renewed$(RESET)"

# Database operations
db-shell:
	@echo "$(GREEN)🗄️  Opening database shell...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec database psql -U khazad_user -d khazad_dum

db-migrate:
	@echo "$(GREEN)📊 Running database migrations...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec trading-engine python -c "from src.data_pipeline.storage.database_manager import DatabaseManager; DatabaseManager().initialize_database()"

# Redis operations  
redis-cli:
	@echo "$(GREEN)📦 Opening Redis CLI...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec redis redis-cli

redis-flush:
	@echo "$(YELLOW)⚠️  Flushing Redis cache...$(RESET)"
	docker compose -f $(COMPOSE_FILE) exec redis redis-cli FLUSHALL

# Performance monitoring
perf:
	@echo "$(GREEN)⚡ System performance:$(RESET)"
	@echo "$(YELLOW)📊 Container stats:$(RESET)"
	@docker stats --no-stream
	@echo "$(YELLOW)💾 Disk usage:$(RESET)"
	@df -h
	@echo "$(YELLOW)🧠 Memory usage:$(RESET)"
	@free -h