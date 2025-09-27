#!/usr/bin/env python3
"""
Health Check System for Khazad-dûm Trading Platform
Provides comprehensive health monitoring for all system components
"""

import time
import json
import asyncio
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
try:
    import psycopg2
except ImportError:
    psycopg2 = None
try:
    import redis
except ImportError:
    redis = None
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check result structure"""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class HealthChecker:
    """Comprehensive health checking for all system components"""
    
    def __init__(self):
        self.checks = {
            "database": self.check_database,
            "redis": self.check_redis,
            "trading_engine": self.check_trading_engine,
            "pattern_system": self.check_pattern_system,
            "api_services": self.check_api_services,
            "disk_space": self.check_disk_space,
            "memory": self.check_memory,
        }
    
    async def check_all(self) -> Dict[str, HealthStatus]:
        """Run all health checks concurrently"""
        results = {}
        
        # Run checks concurrently for better performance
        tasks = []
        for check_name, check_func in self.checks.items():
            if asyncio.iscoroutinefunction(check_func):
                tasks.append(check_func())
            else:
                tasks.append(asyncio.to_thread(check_func))
        
        check_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for check_name, result in zip(self.checks.keys(), check_results):
            if isinstance(result, Exception):
                results[check_name] = HealthStatus(
                    service=check_name,
                    status="unhealthy",
                    latency_ms=0,
                    message=f"Health check failed: {str(result)}",
                    details={"error": str(result)},
                    timestamp=datetime.utcnow()
                )
            else:
                results[check_name] = result
        
        return results
    
    def check_database(self) -> HealthStatus:
        """Check database connectivity and performance (SQLite primary)"""
        start_time = time.time()
        
        try:
            # Use SQLite database check (our primary database)
            from src.data_pipeline.storage.database_manager import DatabaseManager
            
            with DatabaseManager() as db:
                # Test basic connectivity
                cursor = db.conn.execute("SELECT 1")
                cursor.fetchone()
                
                # Check table accessibility and get stats
                try:
                    cursor = db.conn.execute("""
                        SELECT 
                            COUNT(*) as total_positions,
                            COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open_positions
                        FROM position_tracking
                    """)
                    position_stats = cursor.fetchone()
                except Exception:
                    # Table might not exist yet
                    position_stats = (0, 0)
                
                # Check recent activity (last 24 hours)
                try:
                    cursor = db.conn.execute("""
                        SELECT COUNT(*) 
                        FROM stock_metrics 
                        WHERE timestamp > datetime('now', '-1 day')
                    """)
                    recent_data = cursor.fetchone()[0]
                except Exception:
                    recent_data = 0
                
                # Get database file size
                import os
                db_size = "unknown"
                try:
                    if hasattr(db, 'db_path') and os.path.exists(db.db_path):
                        size_bytes = os.path.getsize(db.db_path)
                        db_size = f"{size_bytes / (1024*1024):.1f} MB"
                except Exception:
                    pass
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine status based on performance
            if latency_ms > 1000:
                status = "degraded"
                message = "Database responding slowly"
            elif recent_data == 0:
                status = "degraded"
                message = "No recent data updates (may be normal)"
            else:
                status = "healthy"
                message = "Database operational"
            
            return HealthStatus(
                service="database",
                status=status,
                latency_ms=latency_ms,
                message=message,
                details={
                    "database_type": "SQLite",
                    "total_positions": position_stats[0],
                    "open_positions": position_stats[1],
                    "recent_data_points": recent_data,
                    "database_size": db_size
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="database",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Database connection failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_redis(self) -> HealthStatus:
        """Check Redis connectivity and performance"""
        start_time = time.time()
        
        if redis is None:
            return HealthStatus(
                service="redis",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message="Redis client not available (redis package not installed)",
                details={"error": "redis package not installed"},
                timestamp=datetime.utcnow()
            )
        
        try:
            # Get Redis config from environment
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD')  # Optional
            redis_db = int(os.getenv('REDIS_DB', 0))
            
            # Connect to Redis with secure configuration
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                socket_timeout=5,
                decode_responses=True,
                health_check_interval=30
            )
            
            # Check basic connectivity
            r.ping()
            
            # Check memory usage
            memory_info = r.info("memory")
            used_memory = memory_info.get("used_memory_human", "unknown")
            max_memory = memory_info.get("maxmemory_human", "512MB")
            
            # Check key statistics
            key_info = r.info("keyspace")
            total_keys = sum([info.get("keys", 0) for db, info in key_info.items() if db.startswith("db")])
            
            # Performance test
            test_key = "health_check_test"
            r.set(test_key, "test_value", ex=60)
            r.get(test_key)
            r.delete(test_key)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine status
            if latency_ms > 100:
                status = "degraded"
                message = "Redis responding slowly"
            else:
                status = "healthy"
                message = "Redis operational"
            
            return HealthStatus(
                service="redis",
                status=status,
                latency_ms=latency_ms,
                message=message,
                details={
                    "used_memory": used_memory,
                    "max_memory": max_memory,
                    "total_keys": total_keys
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="redis",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_trading_engine(self) -> HealthStatus:
        """Check trading engine core functionality"""
        start_time = time.time()
        
        try:
            # Test imports of core modules
            from src.core.market_analysis.regime_detector import RegimeDetector
            from src.core.stock_screening.stock_filter import StockFilter
            from src.data_pipeline.storage.database_manager import DatabaseManager
            
            # Test regime detection
            regime_detector = RegimeDetector()
            current_regime = regime_detector.get_current_regime()
            
            # Test database connectivity
            db = DatabaseManager()
            
            # Check if TradingAgents is available
            try:
                from tradingagents.graph.trading_graph import TradingAgentsGraph
                tradingagents_available = True
            except ImportError:
                tradingagents_available = False
            
            latency_ms = (time.time() - start_time) * 1000
            
            status = "healthy"
            message = "Trading engine operational"
            
            if not tradingagents_available:
                status = "degraded"
                message = "TradingAgents not available"
            
            return HealthStatus(
                service="trading_engine",
                status=status,
                latency_ms=latency_ms,
                message=message,
                details={
                    "current_regime": current_regime.get("regime", "unknown"),
                    "fear_greed_value": current_regime.get("fear_greed_value", 0),
                    "tradingagents_available": tradingagents_available
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="trading_engine",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Trading engine check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_pattern_system(self) -> HealthStatus:
        """Check pattern recognition system"""
        start_time = time.time()
        
        try:
            # Test pattern system components
            from src.core.pattern_recognition.pattern_tracker import PatternTracker
            from src.core.pattern_recognition.pattern_classifier import PatternClassifier
            
            # Quick pattern system test
            pattern_tracker = PatternTracker()
            pattern_stats = pattern_tracker.get_pattern_summary()
            
            latency_ms = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service="pattern_system",
                status="healthy",
                latency_ms=latency_ms,
                message="Pattern system operational",
                details={
                    "active_patterns": len(pattern_stats),
                    "pattern_tracker_available": True
                },
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="pattern_system",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Pattern system check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_api_services(self) -> HealthStatus:
        """Check external API connectivity"""
        start_time = time.time()
        apis_status = {}
        
        # Check CNN Fear & Greed (no auth required)
        try:
            response = requests.get(
                "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                timeout=10
            )
            apis_status["cnn_fear_greed"] = response.status_code == 200
        except:
            apis_status["cnn_fear_greed"] = False
        
        # Note: We don't test authenticated APIs in health checks to avoid quota usage
        
        latency_ms = (time.time() - start_time) * 1000
        
        if apis_status.get("cnn_fear_greed", False):
            status = "healthy"
            message = "API services accessible"
        else:
            status = "degraded"
            message = "Some API services unavailable"
        
        return HealthStatus(
            service="api_services",
            status=status,
            latency_ms=latency_ms,
            message=message,
            details=apis_status,
            timestamp=datetime.utcnow()
        )
    
    def check_disk_space(self) -> HealthStatus:
        """Check disk space availability"""
        import shutil
        start_time = time.time()
        
        try:
            # Check disk space for critical directories
            disk_stats = {}
            critical_paths = ["/", "/home/khazad/app/logs", "/home/khazad/app/data"]
            
            for path in critical_paths:
                try:
                    total, used, free = shutil.disk_usage(path)
                    free_pct = (free / total) * 100
                    disk_stats[path] = {
                        "free_gb": round(free / (1024**3), 2),
                        "total_gb": round(total / (1024**3), 2),
                        "free_percent": round(free_pct, 1)
                    }
                except:
                    disk_stats[path] = {"error": "Cannot access path"}
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Check if any disk is critically low
            min_free_pct = min([stat.get("free_percent", 100) for stat in disk_stats.values() if "error" not in stat])
            
            if min_free_pct < 5:
                status = "unhealthy"
                message = "Critical disk space low"
            elif min_free_pct < 15:
                status = "degraded"
                message = "Disk space getting low"
            else:
                status = "healthy"
                message = "Disk space sufficient"
            
            return HealthStatus(
                service="disk_space",
                status=status,
                latency_ms=latency_ms,
                message=message,
                details=disk_stats,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="disk_space",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Disk check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_memory(self) -> HealthStatus:
        """Check system memory usage"""
        import psutil
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_details = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "swap_used_percent": swap.percent
            }
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine status based on memory usage
            if memory.percent > 90 or swap.percent > 80:
                status = "unhealthy"
                message = "Critical memory usage"
            elif memory.percent > 80 or swap.percent > 60:
                status = "degraded"
                message = "High memory usage"
            else:
                status = "healthy"
                message = "Memory usage normal"
            
            return HealthStatus(
                service="memory",
                status=status,
                latency_ms=latency_ms,
                message=message,
                details=memory_details,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return HealthStatus(
                service="memory",
                status="unhealthy",
                latency_ms=(time.time() - start_time) * 1000,
                message=f"Memory check failed: {str(e)}",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )


async def health_check_endpoint() -> Dict[str, Any]:
    """Main health check endpoint that returns JSON status"""
    checker = HealthChecker()
    results = await checker.check_all()
    
    # Calculate overall system status
    all_statuses = [result.status for result in results.values()]
    if "unhealthy" in all_statuses:
        overall_status = "unhealthy"
    elif "degraded" in all_statuses:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    # Calculate average latency
    avg_latency = sum([result.latency_ms for result in results.values()]) / len(results)
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": int(time.time()),  # Will be improved with actual uptime tracking
        "average_latency_ms": round(avg_latency, 2),
        "services": {
            name: {
                "status": result.status,
                "latency_ms": result.latency_ms,
                "message": result.message,
                "details": result.details,
                "timestamp": result.timestamp.isoformat()
            }
            for name, result in results.items()
        }
    }


if __name__ == "__main__":
    # Can be run standalone for testing
    async def main():
        result = await health_check_endpoint()
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())