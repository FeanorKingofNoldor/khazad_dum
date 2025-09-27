"""
██╗  ██╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██║ ██╔╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
█████╔╝ ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██╔═██╗ ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
██║  ██╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: Security Management & Authentication                                │
│ 📄 FILE: security_manager.py                                                   │
│ 📅 CREATED: 2024-12-21                                                             │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ Comprehensive security management with authentication & authorization              │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - hashlib & hmac (password hashing/comparison)                                    │
│ - secrets (secure random generation)                                              │
│ - SQLite (user & session management)                                              │
│ - structured logging (security events)                                            │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: Security Layer (All Stages)                          │
│ └── 1. Market Regime Detection                                                     │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation                                                     │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - PBKDF2 password hashing with 100k iterations                                   │
│ - Session management with timeout & IP tracking                                   │
│ - Brute force protection with account lockout                                     │
│ - Comprehensive security audit logging                                             │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - Password hashing: ~100ms (intentionally slow)                                  │
│ - Session validation: ~1-5ms                                                      │
│ - Automatic session cleanup and timeouts                                          │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_security_manager.py                                 │
│ - Security Tests: tests/security/test_authentication.py                          │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Security Guide: docs/guides/SECURITY_MANAGEMENT.md                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""

import hashlib
import hmac
import secrets
import os
import time
import json
import logging
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from functools import wraps
import sqlite3

from config.logging.logging_config import log_security_event

logger = logging.getLogger('security.manager')


@dataclass
class SecurityContext:
    """Security context for operations"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    permissions: List[str] = None
    authenticated: bool = False
    last_activity: Optional[datetime] = None
    ip_address: Optional[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.last_activity is None:
            self.last_activity = datetime.now()


class SecurityError(Exception):
    """Security-related errors"""
    pass


class AuthenticationError(SecurityError):
    """Authentication failures"""
    pass


class AuthorizationError(SecurityError):
    """Authorization failures"""
    pass


class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize security manager with configuration"""
        self.config = config or {}
        self._sessions: Dict[str, SecurityContext] = {}
        self._failed_attempts: Dict[str, List[datetime]] = {}
        self._blocked_ips: Dict[str, datetime] = {}
        
        # Security configuration
        self.session_timeout = timedelta(hours=self.config.get('session_timeout_hours', 8))
        self.max_failed_attempts = self.config.get('max_failed_attempts', 5)
        self.lockout_duration = timedelta(minutes=self.config.get('lockout_duration_minutes', 30))
        self.password_min_length = self.config.get('password_min_length', 12)
        
        # Initialize security database
        self._init_security_db()
    
    def _init_security_db(self):
        """Initialize security database for user management"""
        try:
            # Use separate security database
            security_db_path = self.config.get('security_db_path', 'config/security/security.db')
            os.makedirs(os.path.dirname(security_db_path), exist_ok=True)
            
            self.security_conn = sqlite3.connect(security_db_path)
            self.security_conn.execute("PRAGMA foreign_keys = ON")
            
            # Create users table
            self.security_conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                permissions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            """)
            
            # Create sessions table
            self.security_conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """)
            
            # Create audit log
            self.security_conn.execute("""
            CREATE TABLE IF NOT EXISTS security_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                details TEXT,
                severity TEXT DEFAULT 'INFO'
            )
            """)
            
            self.security_conn.commit()
            
            # Create default admin user if none exists
            self._create_default_admin_user()
            
            logger.info("Security database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security database: {e}")
            raise SecurityError(f"Security database initialization failed: {e}")
    
    def _create_default_admin_user(self):
        """Create default admin user if none exists"""
        try:
            cursor = self.security_conn.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Generate secure random password
                default_password = secrets.token_urlsafe(16)
                
                self.create_user(
                    username='admin',
                    password=default_password,
                    permissions=['admin', 'trading', 'view_logs', 'manage_users']
                )
                
                # Log the default credentials (WARNING: Only for initial setup)
                logger.warning(f"DEFAULT ADMIN USER CREATED - Username: admin, Password: {default_password}")
                logger.warning("CHANGE DEFAULT PASSWORD IMMEDIATELY")
                
                # Write credentials to secure file
                creds_file = Path('config/security/default_credentials.txt')
                creds_file.parent.mkdir(parents=True, exist_ok=True)
                creds_file.write_text(f"Default Admin Credentials\nUsername: admin\nPassword: {default_password}\n\nCHANGE IMMEDIATELY")
                creds_file.chmod(0o600)  # Owner read/write only
                
        except Exception as e:
            logger.error(f"Failed to create default admin user: {e}")
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        try:
            computed_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(stored_hash, computed_hash)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def create_user(self, username: str, password: str, permissions: List[str]) -> str:
        """Create new user account"""
        try:
            # Validate password strength
            if not self._validate_password_strength(password):
                raise SecurityError("Password does not meet security requirements")
            
            # Generate user ID and hash password
            user_id = secrets.token_urlsafe(16)
            password_hash, salt = self.hash_password(password)
            
            # Store user
            self.security_conn.execute("""
            INSERT INTO users (user_id, username, password_hash, salt, permissions)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, password_hash, salt, json.dumps(permissions)))
            
            self.security_conn.commit()
            
            self._audit_log('user_created', user_id, details={'username': username, 'permissions': permissions})
            logger.info(f"User created: {username}")
            
            return user_id
            
        except sqlite3.IntegrityError:
            raise SecurityError(f"Username '{username}' already exists")
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise SecurityError(f"User creation failed: {e}")
    
    def authenticate_user(self, username: str, password: str, ip_address: Optional[str] = None) -> Optional[SecurityContext]:
        """Authenticate user and create session"""
        try:
            # Check if IP is blocked
            if ip_address and self._is_ip_blocked(ip_address):
                log_security_event('authentication_blocked_ip', f"Blocked IP attempted login: {ip_address}")
                raise AuthenticationError("Access denied")
            
            # Get user from database
            cursor = self.security_conn.execute("""
            SELECT user_id, password_hash, salt, permissions, failed_login_attempts, locked_until
            FROM users WHERE username = ? AND is_active = 1
            """, (username,))
            
            user_row = cursor.fetchone()
            if not user_row:
                self._handle_failed_login(username, ip_address, 'user_not_found')
                raise AuthenticationError("Invalid credentials")
            
            user_id, stored_hash, salt, permissions_json, failed_attempts, locked_until = user_row
            
            # Check if user is locked
            if locked_until:
                lock_time = datetime.fromisoformat(locked_until)
                if datetime.now() < lock_time:
                    self._audit_log('authentication_locked_user', user_id, ip_address=ip_address)
                    raise AuthenticationError("Account is temporarily locked")
            
            # Verify password
            if not self.verify_password(password, stored_hash, salt):
                self._handle_failed_login(username, ip_address, 'invalid_password', user_id)
                raise AuthenticationError("Invalid credentials")
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            permissions = json.loads(permissions_json)
            
            context = SecurityContext(
                user_id=user_id,
                session_id=session_id,
                permissions=permissions,
                authenticated=True,
                ip_address=ip_address
            )
            
            self._sessions[session_id] = context
            
            # Store session in database
            self.security_conn.execute("""
            INSERT INTO sessions (session_id, user_id, last_activity, ip_address)
            VALUES (?, ?, ?, ?)
            """, (session_id, user_id, datetime.now().isoformat(), ip_address))
            
            # Reset failed attempts and update last login
            self.security_conn.execute("""
            UPDATE users SET failed_login_attempts = 0, locked_until = NULL, last_login = ?
            WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            
            self.security_conn.commit()
            
            self._audit_log('authentication_success', user_id, session_id, ip_address)
            logger.info(f"User authenticated successfully: {username}")
            
            return context
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError("Authentication failed")
    
    def _handle_failed_login(self, username: str, ip_address: Optional[str], reason: str, user_id: Optional[str] = None):
        """Handle failed login attempts"""
        try:
            # Log the failed attempt
            self._audit_log('authentication_failed', user_id, ip_address=ip_address, 
                          details={'username': username, 'reason': reason})
            
            if user_id:
                # Increment failed attempts for user
                cursor = self.security_conn.execute("""
                SELECT failed_login_attempts FROM users WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    failed_attempts = row[0] + 1
                    
                    # Lock account if too many failures
                    locked_until = None
                    if failed_attempts >= self.max_failed_attempts:
                        locked_until = (datetime.now() + self.lockout_duration).isoformat()
                        log_security_event('account_locked', f"Account locked after {failed_attempts} failed attempts", 
                                         {'user_id': user_id, 'username': username})
                    
                    self.security_conn.execute("""
                    UPDATE users SET failed_login_attempts = ?, locked_until = ?
                    WHERE user_id = ?
                    """, (failed_attempts, locked_until, user_id))
                    
                    self.security_conn.commit()
            
            # Track IP-based failures
            if ip_address:
                if ip_address not in self._failed_attempts:
                    self._failed_attempts[ip_address] = []
                
                self._failed_attempts[ip_address].append(datetime.now())
                
                # Clean old attempts (older than 1 hour)
                cutoff = datetime.now() - timedelta(hours=1)
                self._failed_attempts[ip_address] = [
                    attempt for attempt in self._failed_attempts[ip_address] 
                    if attempt > cutoff
                ]
                
                # Block IP if too many failures
                if len(self._failed_attempts[ip_address]) >= self.max_failed_attempts:
                    self._blocked_ips[ip_address] = datetime.now() + self.lockout_duration
                    log_security_event('ip_blocked', f"IP blocked after multiple failed attempts: {ip_address}")
                    
        except Exception as e:
            logger.error(f"Error handling failed login: {e}")
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        if ip_address not in self._blocked_ips:
            return False
        
        unblock_time = self._blocked_ips[ip_address]
        if datetime.now() >= unblock_time:
            # Unblock expired IPs
            del self._blocked_ips[ip_address]
            return False
        
        return True
    
    def validate_session(self, session_id: str) -> Optional[SecurityContext]:
        """Validate session and return security context"""
        try:
            if not session_id or session_id not in self._sessions:
                return None
            
            context = self._sessions[session_id]
            
            # Check session timeout
            if datetime.now() - context.last_activity > self.session_timeout:
                self.invalidate_session(session_id)
                return None
            
            # Update last activity
            context.last_activity = datetime.now()
            
            # Update session in database
            self.security_conn.execute("""
            UPDATE sessions SET last_activity = ? WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            self.security_conn.commit()
            
            return context
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def invalidate_session(self, session_id: str):
        """Invalidate session"""
        try:
            if session_id in self._sessions:
                context = self._sessions[session_id]
                del self._sessions[session_id]
                
                # Mark session as inactive in database
                self.security_conn.execute("""
                UPDATE sessions SET is_active = 0 WHERE session_id = ?
                """, (session_id,))
                self.security_conn.commit()
                
                self._audit_log('session_invalidated', context.user_id, session_id)
                
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")
    
    def require_permission(self, permission: str):
        """Decorator to require specific permission"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get session from context (implementation depends on framework)
                session_id = kwargs.get('session_id') or getattr(args[0], 'session_id', None) if args else None
                
                if not session_id:
                    raise AuthorizationError("No session provided")
                
                context = self.validate_session(session_id)
                if not context or not context.authenticated:
                    raise AuthorizationError("Authentication required")
                
                if permission not in context.permissions:
                    self._audit_log('authorization_failed', context.user_id, context.session_id,
                                  details={'required_permission': permission, 'user_permissions': context.permissions})
                    raise AuthorizationError(f"Permission '{permission}' required")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < self.password_min_length:
            return False
        
        # Check for different character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])
    
    def _audit_log(self, event_type: str, user_id: Optional[str] = None, session_id: Optional[str] = None, 
                   ip_address: Optional[str] = None, details: Optional[Dict] = None, severity: str = 'INFO'):
        """Log security event to audit trail"""
        try:
            self.security_conn.execute("""
            INSERT INTO security_audit_log (event_type, user_id, session_id, ip_address, details, severity)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (event_type, user_id, session_id, ip_address, 
                  json.dumps(details) if details else None, severity))
            self.security_conn.commit()
            
            # Also log to structured logging
            log_security_event(event_type, f"Security event: {event_type}", {
                'user_id': user_id,
                'session_id': session_id,
                'ip_address': ip_address,
                'details': details,
                'severity': severity
            })
            
        except Exception as e:
            logger.error(f"Audit logging failed: {e}")
    
    def get_audit_logs(self, hours: int = 24, event_types: Optional[List[str]] = None) -> List[Dict]:
        """Get security audit logs"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            
            query = "SELECT * FROM security_audit_log WHERE timestamp > ?"
            params = [cutoff.isoformat()]
            
            if event_types:
                placeholders = ','.join('?' for _ in event_types)
                query += f" AND event_type IN ({placeholders})"
                params.extend(event_types)
            
            query += " ORDER BY timestamp DESC LIMIT 1000"
            
            cursor = self.security_conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            
            logs = []
            for row in cursor.fetchall():
                log_entry = dict(zip(columns, row))
                if log_entry['details']:
                    log_entry['details'] = json.loads(log_entry['details'])
                logs.append(log_entry)
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            cutoff = datetime.now() - self.session_timeout
            
            # Remove from memory
            expired_sessions = [
                session_id for session_id, context in self._sessions.items()
                if context.last_activity < cutoff
            ]
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
            
            # Mark as inactive in database
            self.security_conn.execute("""
            UPDATE sessions SET is_active = 0 
            WHERE last_activity < ? AND is_active = 1
            """, (cutoff.isoformat(),))
            
            self.security_conn.commit()
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
    
    def get_system_security_status(self) -> Dict[str, Any]:
        """Get overall system security status"""
        try:
            status = {
                'active_sessions': len(self._sessions),
                'blocked_ips': len(self._blocked_ips),
                'failed_attempt_tracking': len(self._failed_attempts),
                'security_events_last_24h': len(self.get_audit_logs(24)),
                'last_security_check': datetime.now().isoformat()
            }
            
            # Get user statistics
            cursor = self.security_conn.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN locked_until IS NOT NULL AND locked_until > datetime('now') THEN 1 END) as locked_users,
                COUNT(CASE WHEN last_login > datetime('now', '-7 days') THEN 1 END) as active_users_7d
            FROM users WHERE is_active = 1
            """)
            
            user_stats = cursor.fetchone()
            if user_stats:
                status.update({
                    'total_users': user_stats[0],
                    'locked_users': user_stats[1],
                    'active_users_7d': user_stats[2]
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get security status: {e}")
            return {'error': str(e)}
    
    def close(self):
        """Clean up security manager resources"""
        try:
            if hasattr(self, 'security_conn'):
                self.security_conn.close()
            self._sessions.clear()
            self._failed_attempts.clear()
            self._blocked_ips.clear()
            logger.info("Security manager closed")
        except Exception as e:
            logger.error(f"Error closing security manager: {e}")


# Global security manager instance
_security_manager = None

def get_security_manager(config: Optional[Dict] = None) -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(config)
    return _security_manager


def require_authentication(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = kwargs.get('session_id') or getattr(args[0], 'session_id', None) if args else None
        
        if not session_id:
            raise AuthorizationError("Authentication required")
        
        security_manager = get_security_manager()
        context = security_manager.validate_session(session_id)
        
        if not context or not context.authenticated:
            raise AuthorizationError("Invalid or expired session")
        
        # Add security context to kwargs
        kwargs['security_context'] = context
        return func(*args, **kwargs)
    
    return wrapper


def require_admin(func):
    """Decorator to require admin permission"""
    @wraps(func)
    @require_authentication
    def wrapper(*args, **kwargs):
        context = kwargs.get('security_context')
        if 'admin' not in context.permissions:
            raise AuthorizationError("Admin permission required")
        return func(*args, **kwargs)
    return wrapper