"""
Structured Logging Configuration for KHAZAD_DUM Trading System
Provides security-aware, JSON-structured logging with proper log rotation and filtering
"""

import logging
import logging.config
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class SecurityFilter(logging.Filter):
    """Filter out potentially sensitive information from logs"""
    
    SENSITIVE_PATTERNS = [
        'password', 'token', 'secret', 'key', 'auth',
        'credential', 'session', 'cookie'
    ]
    
    def filter(self, record):
        """Filter out records containing sensitive information"""
        try:
            # Check message content
            message = record.getMessage().lower()
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in message:
                    # Replace sensitive info with placeholder
                    record.msg = record.msg.replace(
                        record.args[0] if record.args else '',
                        '[REDACTED]'
                    )
                    break
            
            # Check for potential SQL injection patterns
            if 'select' in message and ('union' in message or 'drop' in message):
                record.msg = '[POTENTIAL_SQL_INJECTION_ATTEMPT_BLOCKED]'
            
            return True
        except Exception:
            # Don't fail logging due to filter errors
            return True


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'pathname', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process',
                          'module', 'filename', 'levelno', 'levelname',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = str(value)
        
        return json.dumps(log_entry, default=str)


class TradingLoggerAdapter(logging.LoggerAdapter):
    """Adapter to add trading-specific context to logs"""
    
    def __init__(self, logger, extra_context: Optional[Dict] = None):
        super().__init__(logger, extra_context or {})
        
    def process(self, msg, kwargs):
        """Add trading context to log messages"""
        # Add default trading context
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        kwargs['extra'].update(self.extra)
        kwargs['extra']['component'] = 'trading_system'
        
        return msg, kwargs


def setup_logging_directories():
    """Create necessary logging directories"""
    log_dirs = [
        'logs',
        'logs/trading',
        'logs/patterns',
        'logs/performance',
        'logs/security',
        'logs/archive'
    ]
    
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)


def get_logging_config() -> Dict[str, Any]:
    """Get comprehensive logging configuration"""
    
    # Ensure log directories exist
    setup_logging_directories()
    
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Get environment (production, development, testing)
    environment = os.getenv('ENVIRONMENT', 'development')
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        
        'formatters': {
            'json': {
                '()': JsonFormatter,
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        
        'filters': {
            'security': {
                '()': SecurityFilter,
            }
        },
        
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'simple' if environment == 'development' else 'json',
                'stream': sys.stdout,
                'filters': ['security']
            },
            
            'main_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/khazad_dum_main.log',
                'maxBytes': 50 * 1024 * 1024,  # 50MB
                'backupCount': 10,
                'filters': ['security']
            },
            
            'trading_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/trading/trading_decisions.log',
                'maxBytes': 100 * 1024 * 1024,  # 100MB
                'backupCount': 20,
                'filters': ['security']
            },
            
            'pattern_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/patterns/pattern_analysis.log',
                'maxBytes': 50 * 1024 * 1024,  # 50MB
                'backupCount': 15,
                'filters': ['security']
            },
            
            'performance_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/performance/performance_metrics.log',
                'maxBytes': 30 * 1024 * 1024,  # 30MB
                'backupCount': 12,
                'filters': ['security']
            },
            
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'json',
                'filename': 'logs/security/security_events.log',
                'maxBytes': 20 * 1024 * 1024,  # 20MB
                'backupCount': 50,  # Keep more security logs
            },
            
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/errors.log',
                'maxBytes': 20 * 1024 * 1024,  # 20MB
                'backupCount': 10,
                'filters': ['security']
            }
        },
        
        'loggers': {
            # Root logger
            '': {
                'level': log_level,
                'handlers': ['console', 'main_file', 'error_file'],
                'propagate': False
            },
            
            # Trading-specific loggers
            'trading': {
                'level': 'INFO',
                'handlers': ['trading_file', 'console'],
                'propagate': False
            },
            
            'patterns': {
                'level': 'INFO',
                'handlers': ['pattern_file', 'console'],
                'propagate': False
            },
            
            'performance': {
                'level': 'INFO',
                'handlers': ['performance_file', 'console'],
                'propagate': False
            },
            
            'security': {
                'level': 'WARNING',
                'handlers': ['security_file', 'console'],
                'propagate': False
            },
            
            # Component-specific loggers
            'database': {
                'level': 'INFO',
                'handlers': ['main_file', 'console'],
                'propagate': False
            },
            
            'portfolio': {
                'level': 'INFO',
                'handlers': ['trading_file', 'console'],
                'propagate': False
            },
            
            'regime_detector': {
                'level': 'INFO',
                'handlers': ['trading_file', 'console'],
                'propagate': False
            },
            
            # Third-party loggers (reduce noise)
            'urllib3': {
                'level': 'WARNING',
                'handlers': ['main_file'],
                'propagate': False
            },
            
            'requests': {
                'level': 'WARNING',
                'handlers': ['main_file'],
                'propagate': False
            },
            
            'yfinance': {
                'level': 'WARNING',
                'handlers': ['main_file'],
                'propagate': False
            }
        }
    }
    
    return config


def setup_logging():
    """Setup structured logging for the entire application"""
    try:
        config = get_logging_config()
        logging.config.dictConfig(config)
        
        # Log the logging setup
        logger = logging.getLogger(__name__)
        logger.info("Structured logging system initialized successfully")
        
        return True
        
    except Exception as e:
        # Fallback to basic logging if structured setup fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/fallback.log', mode='a')
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to setup structured logging, using fallback: {e}")
        
        return False


def get_trading_logger(name: str, extra_context: Optional[Dict] = None) -> TradingLoggerAdapter:
    """Get a trading-specific logger with context"""
    logger = logging.getLogger(f"trading.{name}")
    return TradingLoggerAdapter(logger, extra_context or {})


def log_security_event(event_type: str, message: str, details: Optional[Dict] = None):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    security_logger.warning(
        message,
        extra={
            'event_type': event_type,
            'security_event': True,
            'details': details or {}
        }
    )


def log_trading_decision(symbol: str, decision: str, details: Optional[Dict] = None):
    """Log trading decisions with structured data"""
    trading_logger = logging.getLogger('trading')
    trading_logger.info(
        f"Trading decision for {symbol}: {decision}",
        extra={
            'symbol': symbol,
            'decision': decision,
            'trading_event': True,
            'details': details or {}
        }
    )


def log_performance_metric(metric_name: str, value: float, details: Optional[Dict] = None):
    """Log performance metrics"""
    perf_logger = logging.getLogger('performance')
    perf_logger.info(
        f"Performance metric: {metric_name} = {value}",
        extra={
            'metric_name': metric_name,
            'metric_value': value,
            'performance_metric': True,
            'details': details or {}
        }
    )


def log_pattern_event(pattern_id: str, event_type: str, details: Optional[Dict] = None):
    """Log pattern recognition events"""
    pattern_logger = logging.getLogger('patterns')
    pattern_logger.info(
        f"Pattern event: {pattern_id} - {event_type}",
        extra={
            'pattern_id': pattern_id,
            'event_type': event_type,
            'pattern_event': True,
            'details': details or {}
        }
    )


# Initialize logging on import in development
if os.getenv('ENVIRONMENT', 'development') == 'development':
    setup_logging()