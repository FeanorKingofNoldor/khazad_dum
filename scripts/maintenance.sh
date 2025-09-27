#!/bin/bash
# ==============================================================================
# KHAZAD-DÛM AUTOMATED MAINTENANCE SCRIPT
# Production maintenance automation for trading system
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/deploy/backups"
LOG_DIR="$PROJECT_ROOT/logs"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
MAX_BACKUP_AGE_DAYS=30
MAX_LOG_AGE_DAYS=7

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)   echo -e "${RED}[ERROR]${NC} $timestamp - $message" ;;
        WARN)    echo -e "${YELLOW}[WARN]${NC} $timestamp - $message" ;;
        INFO)    echo -e "${GREEN}[INFO]${NC} $timestamp - $message" ;;
        DEBUG)   echo -e "${BLUE}[DEBUG]${NC} $timestamp - $message" ;;
    esac
    
    # Also log to file
    echo "[$level] $timestamp - $message" >> "$LOG_DIR/maintenance.log"
}

# Error handler
error_exit() {
    log ERROR "$1"
    exit 1
}

# Check if running as root (not recommended)
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log WARN "Running as root - this is not recommended for security"
    fi
}

# Ensure required directories exist
setup_directories() {
    log INFO "Setting up required directories..."
    mkdir -p "$BACKUP_DIR" "$LOG_DIR"
    chmod 750 "$BACKUP_DIR" "$LOG_DIR"
}

# Database backup function
backup_database() {
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/$backup_timestamp"
    
    log INFO "Starting database backup to $backup_path"
    
    mkdir -p "$backup_path"
    
    # Database backup
    if docker compose -f "$COMPOSE_FILE" exec -T database pg_isready -U khazad_user; then
        log INFO "Database is ready, starting backup..."
        docker compose -f "$COMPOSE_FILE" exec -T database pg_dump \
            -U khazad_user \
            -d khazad_dum \
            --verbose \
            --no-password \
            | gzip > "$backup_path/database.sql.gz"
        
        if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
            log INFO "Database backup completed successfully"
        else
            error_exit "Database backup failed"
        fi
    else
        error_exit "Database is not ready for backup"
    fi
    
    # Configuration backup
    log INFO "Backing up configurations..."
    cp -r "$PROJECT_ROOT/deploy" "$backup_path/"
    cp "$PROJECT_ROOT/.env" "$backup_path/" 2>/dev/null || log WARN ".env file not found"
    
    # Create backup manifest
    cat > "$backup_path/MANIFEST.txt" << EOF
Khazad-dûm Trading System Backup
================================
Timestamp: $(date)
Database: PostgreSQL dump (gzipped)
Configurations: Nginx, Redis, SSL certificates
Environment: Production settings

Restore Instructions:
1. gunzip database.sql.gz
2. psql -U khazad_user -d khazad_dum < database.sql
3. Copy deploy/ configurations back to project
4. Restart services: make restart

EOF
    
    # Set backup permissions
    chmod -R 640 "$backup_path"
    
    log INFO "Backup completed: $backup_path"
    echo "$backup_path"  # Return path for use by caller
}

# Clean old backups
cleanup_old_backups() {
    log INFO "Cleaning backups older than $MAX_BACKUP_AGE_DAYS days..."
    
    if [[ -d "$BACKUP_DIR" ]]; then
        find "$BACKUP_DIR" -type d -name "20*" -mtime +$MAX_BACKUP_AGE_DAYS -exec rm -rf {} \; 2>/dev/null || true
        
        local remaining_backups=$(find "$BACKUP_DIR" -type d -name "20*" | wc -l)
        log INFO "Backup cleanup completed. $remaining_backups backups remaining."
    fi
}

# Log rotation
rotate_logs() {
    log INFO "Rotating application logs..."
    
    # Application logs
    for logfile in "$LOG_DIR"/*.log; do
        if [[ -f "$logfile" && $(find "$logfile" -mtime +$MAX_LOG_AGE_DAYS) ]]; then
            gzip "$logfile"
            log INFO "Rotated $logfile"
        fi
    done
    
    # Docker container logs (if getting too large)
    docker compose -f "$COMPOSE_FILE" exec -T trading-engine find /home/khazad/app/logs -name "*.log" -size +100M -exec gzip {} \; 2>/dev/null || true
    
    # Clean old compressed logs
    find "$LOG_DIR" -name "*.log.gz" -mtime +$MAX_LOG_AGE_DAYS -delete 2>/dev/null || true
    
    log INFO "Log rotation completed"
}

# System health check
health_check() {
    log INFO "Performing system health check..."
    
    # Container health
    local unhealthy_containers=$(docker compose -f "$COMPOSE_FILE" ps --filter "health=unhealthy" -q | wc -l)
    if [[ $unhealthy_containers -gt 0 ]]; then
        log ERROR "$unhealthy_containers unhealthy containers detected"
        docker compose -f "$COMPOSE_FILE" ps --filter "health=unhealthy"
        return 1
    fi
    
    # Disk space check
    local disk_usage=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 85 ]]; then
        log ERROR "Disk usage is ${disk_usage}% - critically high!"
        return 1
    elif [[ $disk_usage -gt 75 ]]; then
        log WARN "Disk usage is ${disk_usage}% - getting high"
    fi
    
    # Memory usage check
    local mem_usage=$(free | awk 'FNR==2{printf "%.0f", $3/($3+$4)*100}')
    if [[ $mem_usage -gt 90 ]]; then
        log ERROR "Memory usage is ${mem_usage}% - critically high!"
        return 1
    elif [[ $mem_usage -gt 80 ]]; then
        log WARN "Memory usage is ${mem_usage}% - getting high"
    fi
    
    # Application health endpoint
    if curl -sf http://localhost:8000/health >/dev/null; then
        log INFO "Application health check passed"
    else
        log ERROR "Application health check failed"
        return 1
    fi
    
    log INFO "System health check completed successfully"
    return 0
}

# Docker maintenance
docker_maintenance() {
    log INFO "Performing Docker maintenance..."
    
    # Clean unused images, containers, networks
    docker system prune -f >/dev/null 2>&1 || log WARN "Docker system prune failed"
    
    # Remove dangling volumes (be careful!)
    docker volume prune -f >/dev/null 2>&1 || log WARN "Docker volume prune failed"
    
    log INFO "Docker maintenance completed"
}

# SSL certificate check and renewal
check_ssl_certificates() {
    log INFO "Checking SSL certificates..."
    
    local ssl_cert="$PROJECT_ROOT/deploy/ssl/fullchain.pem"
    
    if [[ -f "$ssl_cert" ]]; then
        # Check if certificate expires within 30 days
        if openssl x509 -checkend 2592000 -noout -in "$ssl_cert" >/dev/null; then
            log INFO "SSL certificate is valid for at least 30 more days"
        else
            log WARN "SSL certificate expires within 30 days - renewal needed"
            
            # If using Let's Encrypt, attempt renewal
            if command -v certbot >/dev/null; then
                log INFO "Attempting SSL certificate renewal..."
                certbot renew --quiet && docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
            else
                log WARN "Certbot not found - manual SSL renewal required"
            fi
        fi
    else
        log WARN "SSL certificate not found at $ssl_cert"
    fi
}

# Database maintenance
database_maintenance() {
    log INFO "Performing database maintenance..."
    
    # Update statistics
    docker compose -f "$COMPOSE_FILE" exec -T database psql -U khazad_user -d khazad_dum -c "ANALYZE;" >/dev/null
    
    # Vacuum analyze for performance
    docker compose -f "$COMPOSE_FILE" exec -T database psql -U khazad_user -d khazad_dum -c "VACUUM ANALYZE;" >/dev/null
    
    # Clean old data (adjust based on your retention policy)
    docker compose -f "$COMPOSE_FILE" exec -T database psql -U khazad_user -d khazad_dum -c "
        DELETE FROM stock_metrics WHERE created_at < NOW() - INTERVAL '90 days';
        DELETE FROM api_usage WHERE created_at < NOW() - INTERVAL '30 days';
        DELETE FROM pipeline_decisions WHERE timestamp < NOW() - INTERVAL '60 days';
    " >/dev/null
    
    log INFO "Database maintenance completed"
}

# Main maintenance function
run_maintenance() {
    local maintenance_type="${1:-full}"
    
    log INFO "Starting $maintenance_type maintenance..."
    
    case $maintenance_type in
        "backup")
            backup_database
            ;;
        "cleanup")
            cleanup_old_backups
            rotate_logs
            docker_maintenance
            ;;
        "health")
            health_check
            ;;
        "full")
            # Full maintenance routine
            setup_directories
            
            # Health check first
            if ! health_check; then
                log ERROR "Health check failed - aborting maintenance"
                exit 1
            fi
            
            # Backup before maintenance
            backup_database
            
            # Perform maintenance tasks
            cleanup_old_backups
            rotate_logs
            docker_maintenance
            database_maintenance
            check_ssl_certificates
            
            # Final health check
            if ! health_check; then
                log ERROR "Post-maintenance health check failed"
                exit 1
            fi
            ;;
        *)
            log ERROR "Unknown maintenance type: $maintenance_type"
            echo "Usage: $0 [backup|cleanup|health|full]"
            exit 1
            ;;
    esac
    
    log INFO "$maintenance_type maintenance completed successfully"
}

# Main execution
main() {
    check_permissions
    setup_directories
    
    # Create maintenance lock to prevent concurrent runs
    local lockfile="/tmp/khazad_maintenance.lock"
    exec 200>"$lockfile"
    
    if ! flock -n 200; then
        log ERROR "Another maintenance process is already running"
        exit 1
    fi
    
    # Run maintenance
    run_maintenance "${1:-full}"
    
    # Release lock
    flock -u 200
}

# Run main function with all arguments
main "$@"